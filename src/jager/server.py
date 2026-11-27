"""The webhook server: the only part of Jager that faces the internet.

Zernio POSTs a signed JSON event here whenever you message Jager. Because this
is the one door open to the world, it is built like a nightclub door:

  1. **Fail closed.** No webhook secret configured? The server refuses to start.
     No owner configured? Every message is ignored. Unsure means no.
  2. **Verify the signature** (HMAC-SHA256 of the raw body, per Zernio's docs)
     with a constant-time comparison, BEFORE parsing anything.
  3. **Cap the body** at 1 MiB. Nobody sends us a novel.
  4. **Dedupe** on the event id (Zernio can deliver twice).
  5. **Only the owner** gets a reply. Strangers are logged by id and ignored.
  6. **Answer fast.** Zernio wants a 2xx within 5 seconds, so we acknowledge
     immediately and do the real work in a background task.
  7. **Rate limit** the owner too (30 messages a minute): a runaway loop must
     not burn your AI budget or get your WhatsApp number flagged.
  8. **Say nothing.** Errors never echo internals; /health reveals only "ok".
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import threading
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse

from . import __version__
from .config import ConfigError, Settings
from .core import Jager
from .scheduler import Scheduler

MAX_BODY = 1_048_576          # 1 MiB
RATE_LIMIT = 30               # owner messages per minute


def verify_signature(body: bytes, header: str | None, secret: str) -> bool:
    """Constant-time check of ``X-Zernio-Signature`` (hex HMAC-SHA256 of the raw body).

    ``hmac.compare_digest`` takes the same time whether the first byte or the last
    byte differs, so an attacker cannot guess the signature one character at a time.
    """
    if not header or not secret:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.strip().removeprefix("sha256=").lower())


def _ident(value: str | None) -> str:
    """Normalise ids so '+351 912 345 678', '351912345678' and '@Paul' all compare sanely."""
    v = (value or "").strip().lower().lstrip("@+")
    return re.sub(r"[\s\-()]", "", v)


def is_owner(sender: dict, owner_id: str) -> bool:
    """Does this sender match the configured owner? Empty owner never matches (fail closed)."""
    owner = _ident(owner_id)
    if not owner:
        return False
    candidates = (sender.get("id"), sender.get("phoneNumber"), sender.get("businessScopedUserId"), sender.get("username"))
    return any(_ident(c) == owner for c in candidates if c)


class _RateLimiter:
    def __init__(self, limit: int, per_s: float = 60.0):
        self.limit, self.per, self.hits, self.lock = limit, per_s, deque(), threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self.lock:
            while self.hits and now - self.hits[0] > self.per:
                self.hits.popleft()
            if len(self.hits) >= self.limit:
                return False
            self.hits.append(now)
            return True


def create_app(settings: Settings, jager: Jager | None = None, run_scheduler: bool = True) -> FastAPI:
    if not settings.zernio_webhook_secret:
        raise ConfigError("ZERNIO_WEBHOOK_SECRET is empty. Refusing to start: an unsigned webhook is an open door. "
                          "Pick any long random string, put it in .env and register it with `jager webhook-setup`.")
    j = jager or Jager.from_env()
    limiter = _RateLimiter(RATE_LIMIT)
    sched = Scheduler(j)

    @asynccontextmanager
    async def lifespan(_app):
        if run_scheduler:
            sched.start()
        yield
        sched.stop()

    # docs/openapi disabled: the less a stranger can read about the door, the better.
    app = FastAPI(title="jager", version=__version__, docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.jager = j

    @app.get("/health")
    def health():
        return {"ok": True, "version": __version__}

    @app.post("/webhooks/zernio")
    async def webhook(request: Request, tasks: BackgroundTasks):
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > MAX_BODY:
            return JSONResponse({"error": "too large"}, status_code=413)
        body = await request.body()
        if len(body) > MAX_BODY:
            return JSONResponse({"error": "too large"}, status_code=413)
        if not verify_signature(body, request.headers.get("x-zernio-signature"), settings.zernio_webhook_secret):
            j.store.log("webhook", "bad-signature")
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        try:
            event = json.loads(body)
        except ValueError:
            return JSONResponse({"error": "bad json"}, status_code=400)
        if not isinstance(event, dict):
            return JSONResponse({"error": "bad json"}, status_code=400)

        eid = str(event.get("id") or request.headers.get("x-zernio-event-id") or "")
        if eid and not j.store.first_time(eid):          # duplicate delivery: acknowledge, do nothing
            return {"ok": True, "duplicate": True}
        if event.get("test") or event.get("event") == "webhook.test":
            return {"ok": True}
        if event.get("event") == "message.received":
            tasks.add_task(_on_message, j, settings, limiter, event)
        elif event.get("event") == "comment.received":
            j.store.log("comment.received", "seen", platform=(event.get("comment") or {}).get("platform"))
        return {"ok": True}

    return app


def _on_message(j: Jager, settings: Settings, limiter: _RateLimiter, event: dict) -> None:
    """Runs in the background after we have already said 200 to Zernio."""
    msg = event.get("message") or {}
    if msg.get("direction") != "incoming" or (event.get("metadata") or {}).get("standby"):
        return                                           # our own echo, or someone else's conversation
    sender = msg.get("sender") or {}
    if not is_owner(sender, settings.owner_id):
        j.store.log("message", "ignored-stranger", platform=msg.get("platform"), sender=_ident(str(sender.get("id")))[:12])
        return
    if not limiter.allow():
        j.store.log("message", "rate-limited")
        return
    account_id = (event.get("account") or {}).get("accountId") or (event.get("account") or {}).get("id") or ""
    conv_id = msg.get("conversationId") or ""
    if not account_id or not conv_id:
        j.store.log("message", "no-route")
        return
    j.store.set("chat", {"account_id": account_id, "conversation_id": conv_id})   # remember where to talk to the owner
    _bind_channel(j)
    text = (msg.get("text") or "").strip()
    if not text:
        return
    first_contact = not j.store.get("introduced", False)
    replies = ([j.t("hello")] if first_contact else []) + j.handle(text)
    j.store.set("introduced", True)
    for part in replies[:4]:                             # WhatsApp rejects bursts: keep chat replies few
        j.api.send_message(account_id, conv_id, part[:3500])


def _bind_channel(j: Jager) -> None:
    """Teach Jager where the owner's chat lives so the scheduler can message them proactively."""
    chat = j.store.get("chat")
    if chat:
        j._send = lambda text: j.api.send_message(chat["account_id"], chat["conversation_id"], text[:3500])
