"""The heart of Jager: conversation, confirmations and sprints.

If you only read one file, read this one. The shape of it:

    handle(text)  ->  [replies]
        1. Is a confirmation waiting?  YES executes it, anything else cancels it.
        2. Parse the message (rules first, AI only if the rules shrug).
        3. Dispatch to a small method per intent.

The golden rules (each has a test in tests/test_safety.py):

    * NOTHING is deleted without an explicit YES from the owner, in the chat,
      within ``confirm_ttl_s`` seconds. One question at a time.
    * We check the capability matrix BEFORE asking, so Jager never promises
      what the network will refuse.
    * Dry run is the default. In dry run every "delete" is a polite pretence.
    * Every proposed, confirmed, executed and failed action goes in the log.
    * Destructive calls are paced and batched. We are guests on these networks.

The only mutable "session" state lives in the Store (SQLite), never in Python
variables, so a restart mid-sprint loses nothing. Stability is just memory
that survives a reboot.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from . import capabilities as cap
from .brain import Brain
from .config import Settings, in_quiet_hours, parse_quiet
from .i18n import tr
from .intents import MAX_INPUT, parse
from .mock import MockZernio
from .models import Comment, Intent, Post
from .store import Store
from .zernio import SocialAPI, ZernioClient, ZernioError, iter_posts

SNIPPET = 70           # characters of a post shown in chat
MAX_LISTING = 20       # posts shown in a recap (a chat message is not a spreadsheet)
MAX_SPRINT = 15        # comments per sprint (sprints are short on purpose)

_SPAM = re.compile(r"(https?://|www\.|\bbuy\b|\bcrypto\b|\bfollow me\b|\bdm me\b|\bgiveaway\b|\bpromo\b|\bclick\b)", re.I)
_PRAISE = re.compile(r"\b(congrats?|bravo|love|great|awesome|amazing|merci|felicitations|genial|top)\b", re.I)
_TROLL = re.compile(r"\b(worst|trash|garbage|idiot|stupid|cringe|nul|nulle|ferme ta)\b", re.I)


def classify_rules(text: str) -> str:
    """AI-free triage. Crude on purpose: it only decides what to show first, never what to do."""
    if _SPAM.search(text):
        return "spam"
    if _TROLL.search(text):
        return "troll"
    if "?" in text:
        return "question"
    if _PRAISE.search(text):
        return "praise"
    return "reply"


class Jager:
    def __init__(self, settings: Settings, api: SocialAPI, store: Store | None = None, brain: Brain | None = None,
                 send: Callable[[str], None] | None = None, sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], datetime] | None = None):
        self.s, self.api = settings, api
        self.store = store or Store(settings.db_path)
        self.brain = brain if brain is not None else (Brain(settings, self.store) if settings.openrouter_api_key else None)
        self._send, self._sleep = send, sleep
        self._now = clock or (lambda: datetime.now(UTC))
        self._lock = threading.RLock()        # one conversation at a time: sprints must not interleave
        self.lang = settings.language

    # ------------------------------------------------------------ constructors
    @classmethod
    def from_env(cls, **kw) -> Jager:
        """The 3-line entry point: reads ZERNIO_API_KEY, OPENROUTER_API_KEY, ... from the environment."""
        s = Settings.from_env()
        s.require_zernio()
        api = ZernioClient(s.zernio_api_key, s.base_url, pace_s=s.write_pace_s)
        return cls(s, api, **kw)

    @classmethod
    def demo(cls, language: str = "en", **kw) -> Jager:
        """A fully offline Jager talking to a fake Zernio, with an in-memory diary. Zero keys, zero risk."""
        s = Settings(language=language, dry_run=False, write_pace_s=0, batch_pause_s=0, db_path=":memory:")
        kw.setdefault("sleep", lambda _s: None)
        return cls(s, MockZernio(), store=Store(":memory:"), brain=None, **kw)

    # ----------------------------------------------------------------- helpers
    def t(self, key: str, **kw) -> str:
        return tr(self.lang, key, **kw)

    def _local(self) -> datetime:
        return self._now().astimezone(self.s.tz)

    def notify(self, text: str, urgent: bool = False) -> bool:
        """Proactive message to the owner. Respects quiet hours unless urgent. Returns True if sent."""
        if self._send is None:
            return False
        local = self._local()
        if not urgent and in_quiet_hours(local.hour * 60 + local.minute, parse_quiet(self.s.quiet_hours)):
            self.store.log("notify", "deferred", reason="quiet hours")
            return False
        try:
            self._send(text)
            return True
        except Exception as exc:                          # a failed chat send must never crash a sprint
            self.store.log("notify", "error", error=type(exc).__name__)
            return False

    def notify_available(self) -> bool:
        return self._send is not None

    def notify_recap(self) -> bool:
        """Send the weekly message. True if it went out (False if deferred by quiet hours)."""
        body = f"{self.t('weekly')}\n{self.recap_text()}\n\n{self.t('weekly_cta')}"
        return self.notify(body)

    # ============================================================ conversation
    def handle(self, text: str) -> list[str]:
        """Take one message from the owner, return Jager's replies. Thread-safe."""
        with self._lock:
            try:
                return self._handle(text)
            except ZernioError as exc:
                self.store.log("error", "zernio", status=exc.status, code=exc.code)
                return [self.t("error")]
            except Exception as exc:                      # last line of defence: never stay silent, never crash
                self.store.log("error", "unexpected", error=type(exc).__name__)
                return [self.t("error")]

    def _handle(self, text: str) -> list[str]:
        text = text[:MAX_INPUT]
        intent = parse(text)
        paused = self.store.get("paused", False)
        if paused and intent.kind != "resume":
            return [self.t("paused")]

        out: list[str] = []
        pend = self.store.current_pending()
        if pend:
            if intent.kind == "yes":
                return self._execute(pend)
            # Safety rule 2: anything that is not the confirmation cancels it.
            self.store.close_pending(pend["id"], "cancelled")
            self.store.log("confirm", "cancelled", pending=pend["id"], kind=pend["kind"])
            out.append(self.t("cancelled"))
            if intent.kind == "no":
                return out
        elif intent.kind in {"yes", "no"}:
            return [self.t("nothing_pending")]

        if intent.kind == "unknown" and self.brain:       # tier 2: ask the AI, but only now
            ai = self.brain.understand(text)
            if ai and ai.kind != "unknown":
                intent = ai
        self.store.log("intent", "ok", kind=intent.kind, source=intent.source)

        sprint = self.store.get("sprint")
        handler = getattr(self, f"_i_{intent.kind}", None)
        if sprint and intent.kind in {"send", "edit", "hide", "skip", "delete_comment", "stop"}:
            return out + self._sprint_action(intent, text)
        if handler is None:
            key = "unknown_night" if self._local().hour in (0, 1, 2, 3, 4, 5) else "unknown"
            return out + [self.t(key)]
        return out + handler(intent)

    # -------------------------------------------------------------- simple intents
    def _i_help(self, _i: Intent) -> list[str]:
        return [self.t("help")]

    def _i_jagerbomb(self, _i: Intent) -> list[str]:
        return [self.t("jagerbomb")]                       # easter egg

    def _i_status(self, _i: Intent) -> list[str]:
        onoff = lambda b: self.t("on" if b else "off")      # noqa: E731
        return [self.t("status", accounts=len(self.api.accounts()), rules=len(self.store.active_rules()),
                       ai=onoff(bool(self.brain and self.brain.available)), dry=onoff(self.s.dry_run))]

    def _i_pause(self, _i: Intent) -> list[str]:
        self.store.set("paused", True)
        return [self.t("paused")]

    def _i_resume(self, _i: Intent) -> list[str]:
        self.store.set("paused", False)
        return [self.t("resumed")]

    def _i_stop(self, _i: Intent) -> list[str]:
        return [self.t("no_sprint")]

    # ---------------------------------------------------------------- recap
    def _gather(self, since: datetime) -> list[Post]:
        return list(iter_posts(self.api, since))[:MAX_LISTING]

    def _store_listing(self, posts: list[Post]) -> None:
        self.store.set("listing", [{"key": p.key, "id": p.id, "account_id": p.account_id, "platform": p.platform,
                                    "text": p.text, "created": p.created.isoformat()} for p in posts])

    def _line(self, n: int, p: Post) -> str:
        tags = ""
        if not cap.can(p.platform, "delete_post"):
            tags += " " + self.t("tag_nodelete")
        if self.store.is_protected(p.key):
            tags += " " + self.t("tag_kept")
        snippet = p.text if len(p.text) <= SNIPPET else p.text[: SNIPPET - 1] + "…"
        when = p.created.astimezone(self.s.tz).strftime("%a %H:%M")
        return f"{n}. [{cap.NAMES.get(p.platform, p.platform)}] {snippet} ({when}){tags}"

    def recap_text(self, days: int = 7) -> str:
        posts = self._gather(self._now() - timedelta(days=days))
        self._store_listing(posts)
        if not posts:
            return self.t("recap_none")
        lines = [self.t("recap_head"), *(self._line(i, p) for i, p in enumerate(posts, 1)), "", self.t("recap_foot")]
        return "\n".join(lines)

    def _i_recap(self, _i: Intent) -> list[str]:
        return [self.recap_text()]

    def weekly_recap(self) -> str:
        """Library entry point: the Sunday message. Returns the text (and sends it if a channel is wired)."""
        body = f"{self.t('weekly')}\n{self.recap_text()}\n\n{self.t('weekly_cta')}"
        self.notify(body)
        return body

    # --------------------------------------------------------------- deleting
    def _listing(self) -> list[dict]:
        return self.store.get("listing", [])

    def _resolve(self, numbers: list[int]) -> tuple[list[Post], list[str]]:
        """Numbers from the last listing -> deletable Posts, plus human notes about the ones we skip."""
        listing, notes, posts = self._listing(), [], []
        for n in numbers:
            if not 1 <= n <= len(listing):
                notes.append(self.t("bad_number", n=n))
                continue
            r = listing[n - 1]
            if r.get("deleted"):
                notes.append(self.t("already_gone", n=n))        # numbers never shift: #3 stays #3 forever
                continue
            p = Post(r["id"], r["account_id"], r["platform"], r["text"], datetime.fromisoformat(r["created"]))
            if self.store.is_protected(p.key):
                notes.append(self.t("skipped_protected", n=1))
            elif not cap.can(p.platform, "delete_post"):
                notes.append(cap.why_not(p.platform, "delete_post"))   # honest about what we cannot do
            else:
                posts.append(p)
        return posts, notes

    def _propose_delete(self, numbers: list[int]) -> list[str]:
        if not self._listing():
            return [self.t("need_listing")]
        posts, notes = self._resolve(numbers)
        if not posts:
            return [*notes, self.t("nothing_deletable")]
        nums = [n for n in numbers if 1 <= n <= len(self._listing())]
        items = [{"id": p.id, "account_id": p.account_id, "platform": p.platform, "text": p.text,
                  "created": p.created.isoformat()} for p in posts]
        shown = ", ".join(str(n) for n in nums)
        summary = self.t("ask_delete", n=len(posts), nums=shown)
        pid = self.store.open_pending("delete_posts", {"items": items}, summary, self.s.confirm_ttl_s)
        self.store.log("propose", "open", pending=pid, kind="delete_posts", count=len(posts))
        return [*notes, summary]

    def _i_delete(self, i: Intent) -> list[str]:
        return self._propose_delete(i.numbers)

    def _i_delete_all(self, _i: Intent) -> list[str]:
        return self._propose_delete(list(range(1, len(self._listing()) + 1)))

    def _i_keep(self, i: Intent) -> list[str]:
        listing, kept = self._listing(), []
        for n in i.numbers:
            if 1 <= n <= len(listing):
                self.store.protect(listing[n - 1]["key"])
                kept.append(n)
        return [self.t("kept", nums=", ".join(map(str, kept)))] if kept else [self.t("need_listing")]

    # ------------------------------------------------------------------ rules
    def _i_timer(self, i: Intent) -> list[str]:
        accounts = self.api.accounts()
        platforms = sorted({a.platform for a in accounts if cap.can(a.platform, "delete_post")})
        if not platforms:
            return [self.t("rule_nothing")]
        hours, delay = int(i.args.get("hours", 8)), int(i.args.get("delay_min", 60))
        names = ", ".join(cap.NAMES.get(p, p) for p in platforms)
        summary = self.t("ask_rule", hours=hours, delay=delay, platforms=names)
        pid = self.store.open_pending("rule", {"hours": hours, "delay_min": delay, "platforms": platforms},
                                      summary, self.s.confirm_ttl_s)
        self.store.log("propose", "open", pending=pid, kind="rule")
        return [summary]

    _i_night = _i_timer

    def _i_stop_rules(self, _i: Intent) -> list[str]:
        n = self.store.stop_rules()
        self.store.log("rule", "stopped", count=n)
        return [self.t("rules_stopped", n=n)]

    # ---------------------------------------------------------------- execute
    def _execute(self, pend: dict) -> list[str]:
        """The owner said YES to the open confirmation. Do exactly what was shown, nothing more."""
        self.store.close_pending(pend["id"], "confirmed")
        self.store.log("confirm", "yes", pending=pend["id"], kind=pend["kind"])
        kind, payload = pend["kind"], pend["payload"]
        if kind == "delete_posts":
            return [self._run_deletes(payload["items"])]
        if kind == "rule":
            now = self._now().timestamp()
            self.store.add_rule(now, now + payload["hours"] * 3600, payload["delay_min"] * 60, payload["platforms"])
            return [self.t("rule_on")]
        if kind == "delete_comment":
            return self._do_delete_comment(Comment(**payload["comment"]))
        return [self.t("error")]

    def _pace(self, i: int) -> None:
        """Be a polite guest: a short pause after every call, a longer one after every batch."""
        self._sleep(self.s.write_pace_s)
        if (i + 1) % self.s.batch_size == 0:
            self._sleep(self.s.batch_pause_s)

    def _run_deletes(self, items: list[dict]) -> str:
        done, failures = 0, []
        for i, r in enumerate(items):
            post = Post(r["id"], r["account_id"], r["platform"], r["text"], datetime.fromisoformat(r["created"]))
            if self.s.dry_run:
                self.store.log("delete_post", "dry-run", post=post.key)
                done += 1
                continue
            try:
                self.api.delete_post(post)
                self.store.log("delete_post", "ok", post=post.key)
                done += 1
            except ZernioError as exc:
                self.store.log("delete_post", "failed", post=post.key, status=exc.status, code=exc.code)
                failures.append(f"{cap.NAMES.get(post.platform, post.platform)}: {exc}")
            self._pace(i)
        # forget deleted entries so the numbers in the list stay honest
        if not self.s.dry_run and done:
            gone = {r["id"] for r in items}      # flag, never remove: list numbers must not shift under the user's feet
            self.store.set("listing", [r | {"deleted": True} if r["id"] in gone else r for r in self._listing()])
        left = sum(1 for r in self._listing() if not r.get("deleted"))
        msg = self.t("deleted_dry", n=done) if self.s.dry_run else self.t("deleted", n=done, left=left)
        if failures:
            msg += "\n" + self.t("failed", n=len(failures), why="; ".join(failures)[:300])
        return msg

    # ================================================================ comments
    def _collect_comments(self) -> list[Comment]:
        """New, reply-able comments from the last 7 days, newest posts first, capped for sanity."""
        since = self._now() - timedelta(days=7)
        found: list[Comment] = []
        for row in self.api.commented_posts(since, limit=10):
            if not cap.can(row["platform"], "read_comments"):
                continue
            try:
                cs = self.api.comments(row["id"], row["account_id"], row["platform"])
            except ZernioError:
                continue
            found += [c for c in cs if not c.is_own and not c.is_hidden and not self.store.is_handled(c.key)]
            if len(found) >= MAX_SPRINT:
                break
        return found[:MAX_SPRINT]

    def _triage(self, comments: list[Comment]) -> None:
        """Fill in category + draft: AI in one batch if available, plain rules otherwise."""
        ai = self.brain.triage(comments) if self.brain else {}
        for c in comments:
            c.category, c.draft = ai.get(c.key, (classify_rules(c.text), ""))
        order = {"question": 0, "reply": 1, "praise": 2, "troll": 3, "spam": 4, "other": 5}
        comments.sort(key=lambda c: order.get(c.category, 9))     # questions first, spam last

    def _i_comments(self, _i: Intent) -> list[str]:
        cs = self._collect_comments()
        if not cs:
            return [self.t("comments_none")]
        return [self.t("comments_sum", n=len(cs), posts=len({c.post_id for c in cs}))]

    def _i_sprint_comments(self, _i: Intent) -> list[str]:
        cs = self._collect_comments()
        if not cs:
            return [self.t("comments_none")]
        self._triage(cs)
        queue = [c.__dict__ | {"created": c.created.isoformat() if c.created else None} for c in cs]
        self.store.set("sprint", {"queue": queue, "i": 0, "sent": 0, "hid": 0, "dele": 0, "skip": 0})
        self.store.log("sprint", "start", kind="comments", count=len(cs))
        return [self.t("sprint_intro", n=len(cs)), self._sprint_item()]

    def _i_sprint_cleanup(self, _i: Intent) -> list[str]:
        """Old posts: look at the newest 100 per account and show those older than 90 days."""
        cutoff = self._now() - timedelta(days=90)
        old: list[Post] = []
        for acc in self.api.accounts():
            try:
                old += [p for p in self.api.posts(acc, datetime.fromtimestamp(0, UTC), 100) if p.created < cutoff]
            except ZernioError:
                continue
        old = sorted(old, key=lambda p: p.created)[:MAX_LISTING]
        if not old:
            return [self.t("cleanup_none")]
        self._store_listing(old)
        return [self.t("cleanup_head") + "\n" + "\n".join(self._line(n, p) for n, p in enumerate(old, 1)) + "\n\n" + self.t("recap_foot")]

    # ---------------------------------------------------------- sprint stepping
    def _current(self, sp: dict) -> Comment | None:
        if sp["i"] >= len(sp["queue"]):
            return None
        q = dict(sp["queue"][sp["i"]])
        q["created"] = datetime.fromisoformat(q["created"]) if q.get("created") else None
        return Comment(**q)

    def _sprint_item(self) -> str:
        sp = self.store.get("sprint")
        c = self._current(sp)
        if c is None:
            return self._finish_sprint()
        draft = self.t("draft_line", d=c.draft) if c.draft else ""
        text = c.text if len(c.text) <= 200 else c.text[:199] + "…"
        return self.t("sprint_item", platform=cap.NAMES.get(c.platform, c.platform), author=c.author or "?",
                      cat=c.category, text=text, draft=draft)

    def _finish_sprint(self) -> str:
        sp = self.store.get("sprint") or {}
        self.store.delete("sprint")
        self.store.log("sprint", "done", **{k: sp.get(k, 0) for k in ("sent", "hid", "dele", "skip")})
        return self.t("sprint_done", sent=sp.get("sent", 0), hid=sp.get("hid", 0), dele=sp.get("dele", 0), skip=sp.get("skip", 0))

    def _advance(self, field: str | None) -> str:
        sp = self.store.get("sprint")
        if field:
            sp[field] += 1
        sp["i"] += 1
        self.store.set("sprint", sp)
        return self._sprint_item()

    def _sprint_action(self, i: Intent, raw: str) -> list[str]:
        sp = self.store.get("sprint")
        c = self._current(sp)
        if i.kind == "stop" or c is None:
            return [self._finish_sprint()]
        if i.kind == "skip":
            return [self.t("skip"), self._advance("skip")]
        if i.kind in {"send", "edit"}:
            text = i.args.get("text") if i.kind == "edit" else c.draft
            if not text:
                return [self.t("no_draft")]
            # The user has just SEEN this exact text and said send: that is explicit consent for this one reply.
            if not cap.can(c.platform, "reply_comment"):
                return [cap.why_not(c.platform, "reply_comment")]
            if self.s.dry_run:
                self.store.log("reply", "dry-run", comment=c.key)
                return [self.t("sent_dry"), self._advance("sent")]
            self.api.reply(c, text[:1000])
            self.store.mark_handled(c.key)
            self.store.log("reply", "ok", comment=c.key)
            self._sleep(self.s.write_pace_s)
            return [self.t("sent"), self._advance("sent")]
        if i.kind == "hide":
            if not cap.can(c.platform, "hide_comment"):
                return [cap.why_not(c.platform, "hide_comment")]
            if self.s.dry_run:
                self.store.log("hide", "dry-run", comment=c.key)
                return [self.t("hid_dry"), self._advance("hid")]
            self.api.hide_comment(c)
            self.store.mark_handled(c.key)
            self.store.log("hide", "ok", comment=c.key)
            self._sleep(self.s.write_pace_s)
            return [self.t("hid"), self._advance("hid")]
        if i.kind == "delete_comment":
            if not cap.can(c.platform, "delete_comment"):
                return [cap.why_not(c.platform, "delete_comment")]
            payload = {"comment": c.__dict__ | {"created": None}}       # datetime is not JSON; we do not need it to delete
            summary = self.t("ask_delete_comment", who=c.author or "?")
            self.store.open_pending("delete_comment", payload, summary, self.s.confirm_ttl_s)
            return [summary]
        return [self.t("unknown")]

    def _do_delete_comment(self, c: Comment) -> list[str]:
        if self.s.dry_run:
            self.store.log("delete_comment", "dry-run", comment=c.key)
        else:
            try:
                self.api.delete_comment(c)
                self.store.mark_handled(c.key)
                self.store.log("delete_comment", "ok", comment=c.key)
            except ZernioError as exc:
                self.store.log("delete_comment", "failed", comment=c.key, status=exc.status)
                return [str(exc)]
        sp = self.store.get("sprint")
        if sp:
            return [self.t("comment_deleted"), self._advance("dele")]
        return [self.t("comment_deleted")]

    # ----------------------------------------------------------- sprint(kind)
    def sprint(self, kind: str = "comments") -> list[str]:
        """Library entry point: ``jager.sprint("comments")``. Returns Jager's first messages."""
        with self._lock:
            handler = {"comments": self._i_sprint_comments, "cleanup": self._i_sprint_cleanup, "night": self._i_night}.get(kind)
            if handler is None:
                raise ValueError("sprint kind must be 'comments', 'cleanup' or 'night'")
            return handler(Intent(kind))
