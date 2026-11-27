"""The scheduler: Jager's alarm clock and night watchman.

Two jobs, both tiny:

1. **Weekly reminder.** At the configured day and time (default Sunday 10:00,
   in YOUR timezone) Jager sends the recap and offers a sprint.
2. **Auto-delete rules.** While a rule is active ("delete what I post tonight,
   an hour after"), look for posts whose timer has run out and delete them.

Why a plain thread and not APScheduler? Two jobs do not need a framework.
Fewer dependencies means fewer things to update, audit and break.

Stability notes
---------------
* ``tick()`` is a pure-ish function of "now": the thread just calls it every
  few seconds. Tests call it directly with a fake clock. No sleeping in tests.
* The weekly reminder is remembered by ISO week in the database
  (``last_recap_week``). A restart cannot double-send it, and a restart at
  10:05 still sends it (catch-up), unless it is quiet hours, in which case it
  waits until the quiet window ends.
* A rule tick that crashes is logged and retried next time. The thread itself
  never dies: a watchman who quits on the first noise is not a watchman.
* Efficiency: we only poll the networks while a rule is active AND something
  can actually be due. On X every read costs money, so we do not idle-poll.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta

from . import capabilities as cap
from .config import parse_recap
from .core import Jager
from .zernio import ZernioError


class Scheduler:
    def __init__(self, jager: Jager, tick_s: float = 20.0):
        self.j, self.tick_s = jager, tick_s
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_rules_poll = 0.0

    # ---------------------------------------------------------------- thread
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="jager-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.wait(self.tick_s):          # wait() doubles as an interruptible sleep
            try:
                self.tick()
            except Exception as exc:                      # never let the watchman die
                self.j.store.log("scheduler", "error", error=type(exc).__name__)

    # ------------------------------------------------------------------ tick
    def tick(self, now: datetime | None = None) -> None:
        now = now or datetime.now(UTC)
        self._weekly(now)
        self._rules(now)
        if int(now.timestamp()) % 3600 < self.tick_s:     # about once an hour: tidy old dedupe rows
            self.j.store.purge()

    def _weekly(self, now: datetime) -> None:
        wd, hh, mm = parse_recap(self.j.s.recap)
        local = now.astimezone(self.j.s.tz)
        week = local.isocalendar()[:2]                     # (year, week number)
        due = local.replace(hour=hh, minute=mm, second=0, microsecond=0)
        due = due - timedelta(days=(local.weekday() - wd) % 7)
        if local < due or self.j.store.get("last_recap_week") == list(week):
            return
        # Past the scheduled moment and not yet sent this week.
        if self.j.notify_available() and self.j.notify_recap():
            self.j.store.set("last_recap_week", list(week))
            self.j.store.log("weekly", "sent", week=list(week))

    def _rules(self, now: datetime) -> None:
        rules = self.j.store.active_rules()
        if not rules or now.timestamp() - self._last_rules_poll < self.j.s.rule_poll_s:
            return
        self._last_rules_poll = now.timestamp()
        deleted = 0
        for rule in rules:
            if now.timestamp() < rule["starts"] + rule["delay_s"]:
                continue                                    # nothing can be due yet: do not spend API calls
            since = datetime.fromtimestamp(rule["starts"], UTC)
            for acc in self.j.api.accounts():
                if acc.platform not in rule["platforms"] or not cap.can(acc.platform, "delete_post"):
                    continue
                try:
                    posts = self.j.api.posts(acc, since, 50)
                except ZernioError:
                    continue
                for p in posts:
                    t = p.created.timestamp()
                    due = t + rule["delay_s"] <= now.timestamp()
                    if not (rule["starts"] <= t <= rule["ends"] and due):
                        continue
                    if self.j.store.is_handled(p.key) or self.j.store.is_protected(p.key):
                        continue
                    deleted += self._delete_by_rule(p, rule["id"])
        if deleted:
            self.j.notify(self.j.t("rule_ran", n=deleted))

    def _delete_by_rule(self, p, rule_id: int) -> int:
        """The user created this rule with a clear scope and expiry, so no per-post YES is needed."""
        st = self.j.store
        if self.j.s.dry_run:
            st.log("delete_post", "dry-run", post=p.key, rule=rule_id)
            st.mark_handled(p.key)
            return 1
        try:
            self.j.api.delete_post(p)
            st.mark_handled(p.key)
            st.log("delete_post", "ok", post=p.key, rule=rule_id)
            return 1
        except ZernioError as exc:
            st.mark_handled(p.key)                          # do not retry forever on a post the network refuses
            st.log("delete_post", "failed", post=p.key, rule=rule_id, status=exc.status)
            return 0
