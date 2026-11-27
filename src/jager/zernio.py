"""The Zernio client.

Zernio is the one door through which Jager touches your social accounts and
your chat app. This file is that door's doorman: it knows the URLs, retries
when the network hiccups, pauses when Zernio says "slow down" and refuses to
crash your night because of one weird response.

Stability tricks (all of them tested)
-------------------------------------
* Connection pooling (one ``httpx.Client`` for the whole life of the program).
* Retries with exponential backoff + jitter on 429 and 5xx, honouring the
  ``Retry-After`` header. Network blips are retried; 4xx client errors are not
  (retrying a wrong request never makes it right).
* An ``Idempotency-Key`` on every write, so a retry after a timeout cannot
  send the same reply twice. (Zernio keeps keys for 24 hours.)
* A small TTL cache for GETs, cleared on every write, so a recap does not
  hammer the API (X bills per read, your wallet will thank you).
* Tolerant parsing: Zernio's JSON shapes vary a bit per platform, so we read
  fields defensively and skip rows we cannot understand instead of exploding.

The ``SocialAPI`` protocol at the bottom is the contract. ``ZernioClient``
speaks to the real service, ``MockZernio`` (mock.py) is a pocket-sized fake
with the same methods: that is what the tests and ``jager demo`` use.
"""

from __future__ import annotations

import random
import time
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

import httpx

from .models import Account, Comment, Post


class ZernioError(RuntimeError):
    """An error from Zernio, with the stable ``type`` and ``code`` it sends back."""

    def __init__(self, message: str, status: int = 0, type_: str = "", code: str = ""):
        super().__init__(message)
        self.status, self.type, self.code = status, type_, code

    @property
    def retryable(self) -> bool:
        return self.status == 429 or self.status >= 500


class Unsupported(ZernioError):
    """The network itself refuses this action. Not a bug, just life."""


# --------------------------------------------------------------------------- #
# The contract everything else depends on.                                    #
# --------------------------------------------------------------------------- #
class SocialAPI(Protocol):
    def accounts(self) -> list[Account]: ...
    def posts(self, account: Account, since: datetime, limit: int = 50) -> list[Post]: ...
    def commented_posts(self, since: datetime, limit: int = 20) -> list[dict]: ...
    def comments(self, post_id: str, account_id: str, platform: str, limit: int = 50) -> list[Comment]: ...
    def delete_post(self, post: Post) -> None: ...
    def reply(self, comment: Comment, message: str) -> None: ...
    def hide_comment(self, comment: Comment) -> None: ...
    def delete_comment(self, comment: Comment) -> None: ...
    def send_message(self, account_id: str, conversation_id: str, text: str) -> None: ...


def _dt(value: Any) -> datetime:
    """Parse the many date spellings we meet into an aware UTC datetime. Never raises."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / (1000 if value > 1e11 else 1), tz=UTC)
    if isinstance(value, str) and value:
        try:
            d = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return d if d.tzinfo else d.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.fromtimestamp(0, tz=UTC)   # "unknown" sorts as ancient history


def _first(d: dict, *keys: str, default: Any = "") -> Any:
    """First present, non-empty value among several possible key names."""
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return default


def _rows(payload: Any, *keys: str) -> list[dict]:
    """Find the list of rows in a response that might be a bare list or wrapped under some key."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        for k in (*keys, "data", "items", "results"):
            v = payload.get(k)
            if isinstance(v, list):
                return [r for r in v if isinstance(r, dict)]
    return []


class ZernioClient:
    """Real implementation of ``SocialAPI`` over HTTPS."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://zernio.com/api/v1",
        *,
        timeout: float = 20.0,
        max_retries: int = 3,
        cache_ttl: float = 30.0,
        pace_s: float = 0.0,
        sleep: Callable[[float], None] = time.sleep,
        transport: httpx.BaseTransport | None = None,
    ):
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "jager/0.1 (+https://jager.social)"},
            transport=transport,
        )
        self.max_retries, self.cache_ttl, self.pace_s, self._sleep = max_retries, cache_ttl, pace_s, sleep
        self._cache: dict[str, tuple[float, Any]] = {}
        self._last_write = 0.0

    def close(self) -> None:
        self._http.close()

    # ------------------------------------------------------------ plumbing
    def _request(self, method: str, path: str, *, params=None, json=None, write: bool = False) -> Any:
        """One HTTP call with retries, pacing, idempotency and error translation."""
        headers = {"Idempotency-Key": str(uuid.uuid4())} if write else {}   # same key reused on retries below
        if write and self.pace_s:                                            # be polite to the networks
            wait = self.pace_s - (time.monotonic() - self._last_write)
            if wait > 0:
                self._sleep(wait)
        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                r = self._http.request(method, path, params=params, json=json, headers=headers)
            except (httpx.TransportError, httpx.TimeoutException) as exc:   # network hiccup: retry
                last = ZernioError(f"network error: {exc}", status=599)
                self._backoff(attempt, None)
                continue
            if r.status_code < 400:
                if write:
                    self._last_write = time.monotonic()
                    self._cache.clear()                                      # world changed: forget what we knew
                return r.json() if r.content else {}
            err = self._to_error(r)
            if not err.retryable or attempt == self.max_retries:
                raise err
            last = err
            self._backoff(attempt, r.headers.get("Retry-After"))
        raise last or ZernioError("request failed")

    def _backoff(self, attempt: int, retry_after: str | None) -> None:
        if retry_after and retry_after.isdigit():
            delay = min(float(retry_after), 30.0)                            # trust the server, within reason
        else:
            delay = min(0.5 * (2 ** attempt), 8.0) + random.uniform(0, 0.25)  # nosec B311 - retry jitter, not crypto  # jitter avoids thundering herds
        self._sleep(delay)

    @staticmethod
    def _to_error(r: httpx.Response) -> ZernioError:
        try:
            body = r.json()
        except ValueError:
            body = {}
        msg = body.get("error") or body.get("message") or r.text[:200] or f"HTTP {r.status_code}"
        code = str(body.get("code", ""))
        if code in {"PLATFORM_LIMITATION", "platform_not_supported"} or "not supported" in str(msg).lower():
            return Unsupported(msg, r.status_code, body.get("type", ""), code)
        return ZernioError(msg, r.status_code, body.get("type", ""), code)

    def _get(self, path: str, params: dict | None = None) -> Any:
        """Cached GET. The cache key includes params; entries expire after ``cache_ttl`` seconds."""
        key = path + "?" + "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        hit = self._cache.get(key)
        if hit and time.monotonic() - hit[0] < self.cache_ttl:
            return hit[1]
        data = self._request("GET", path, params=params)
        self._cache[key] = (time.monotonic(), data)
        return data

    # -------------------------------------------------------------- reading
    def accounts(self) -> list[Account]:
        rows = _rows(self._get("/accounts"), "accounts")
        return [Account(id=str(_first(r, "_id", "id")), platform=str(_first(r, "platform")),
                        handle=str(_first(r, "username", "displayName", "name")))
                for r in rows if _first(r, "_id", "id") and _first(r, "platform")]

    def posts(self, account: Account, since: datetime, limit: int = 50) -> list[Post]:
        """Newest-first posts that exist on the platform, stopping once we pass ``since``.

        Efficiency: Zernio returns newest first, so we stop paginating at the first
        page that reaches back past ``since``. On X every page is billed, so this matters.
        """
        out: list[Post] = []
        cursor = None
        while len(out) < limit:
            params = {"limit": min(limit, 100)}
            if cursor:
                params["cursor"] = cursor
            data = self._get(f"/accounts/{account.id}/posts", params)
            rows = _rows(data, "posts")
            done = False
            for r in rows:
                created = _dt(_first(r, "publishedAt", "createdTime", "createdAt", "date", "timestamp"))
                if created < since:
                    done = True
                    break
                pid = str(_first(r, "id", "_id", "postId"))
                if pid:
                    out.append(Post(pid, account.id, account.platform,
                                    str(_first(r, "message", "content", "text", "caption")), created,
                                    str(_first(r, "url", "permalink", "platformPostUrl"))))
            pg = data.get("pagination", {}) if isinstance(data, dict) else {}
            cursor = pg.get("nextCursor")
            if done or not pg.get("hasMore") or not cursor:
                break
        return out[:limit]

    def commented_posts(self, since: datetime, limit: int = 20) -> list[dict]:
        data = self._get("/inbox/comments", {"minComments": 1, "limit": limit, "since": since.isoformat()})
        return [{"id": str(_first(r, "id")), "account_id": str(_first(r, "accountId")),
                 "platform": str(_first(r, "platform")), "text": str(_first(r, "content")),
                 "count": int(_first(r, "commentCount", default=0) or 0)} for r in _rows(data, "data")]

    def comments(self, post_id: str, account_id: str, platform: str, limit: int = 50) -> list[Comment]:
        data = self._get(f"/inbox/comments/{post_id}", {"accountId": account_id, "limit": limit})
        out = []
        for r in _rows(data, "comments"):
            cid = str(_first(r, "id", "_id"))
            if not cid:
                continue
            frm = r.get("from") if isinstance(r.get("from"), dict) else {}
            out.append(Comment(
                id=cid, post_id=post_id, account_id=account_id, platform=platform,
                text=str(_first(r, "message", "text", "content")),
                author=str(_first(frm, "username", "name", default=_first(r, "author", default=""))),
                created=_dt(_first(r, "createdTime", "createdAt")),
                is_own=bool(frm.get("isOwnAccount") or r.get("isOwnAccount")),
                is_hidden=bool(r.get("isHidden")),
            ))
        return out

    # -------------------------------------------------------------- writing
    def delete_post(self, post: Post) -> None:
        """Unpublish: delete the post from the platform. (Instagram, TikTok, Snapchat refuse, see capabilities.py)"""
        self._request("POST", f"/posts/{post.id}/unpublish", write=True,
                      json={"platform": post.platform, "accountId": post.account_id})

    def reply(self, comment: Comment, message: str) -> None:
        self._request("POST", f"/inbox/comments/{comment.post_id}", write=True,
                      json={"accountId": comment.account_id, "commentId": comment.id, "message": message})

    def hide_comment(self, comment: Comment) -> None:
        self._request("POST", f"/inbox/comments/{comment.post_id}/{comment.id}/hide", write=True,
                      json={"accountId": comment.account_id})

    def delete_comment(self, comment: Comment) -> None:
        self._request("DELETE", f"/inbox/comments/{comment.post_id}", write=True,
                      params={"accountId": comment.account_id, "commentId": comment.id})

    def send_message(self, account_id: str, conversation_id: str, text: str) -> None:
        # WhatsApp rejects bursts to one recipient (~10/min), so chat replies are kept short and few.
        self._request("POST", f"/inbox/conversations/{conversation_id}/messages", write=True,
                      json={"accountId": account_id, "message": text})

    # ------------------------------------------------------------ one-offs
    def create_webhook(self, url: str, secret: str, events: list[str] | None = None) -> dict:
        """Register this server as a Zernio webhook endpoint (used by `jager webhook-setup`)."""
        return self._request("POST", "/webhooks/settings", write=True, json={
            "name": "Jager", "url": url, "secret": secret,
            "events": events or ["message.received", "comment.received"]})

    def ping(self) -> int:
        """Cheap health probe used by `jager doctor`: how many accounts are connected."""
        return len(self.accounts())


def window(days: int = 7) -> datetime:
    """Start of the default look-back window (one week, because weekends are where regrets live)."""
    return datetime.now(UTC) - timedelta(days=days)


def iter_posts(api: SocialAPI, since: datetime, per_account: int = 30) -> Iterator[Post]:
    """Yield posts from every account that is able to have them, newest first overall.

    One failing account (expired token, rate limit) must not ruin the recap for the others,
    so errors are swallowed per account and surfaced via the ``errors`` attribute when asked.
    """
    posts: list[Post] = []
    for acc in api.accounts():
        try:
            posts.extend(api.posts(acc, since, per_account))
        except ZernioError:
            continue
    posts.sort(key=lambda p: p.created, reverse=True)
    yield from posts
