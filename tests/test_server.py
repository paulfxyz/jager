"""The door: signatures, dedupe, strangers, owner flow, size caps."""
import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from jager import Jager
from jager.config import Settings
from jager.mock import MockZernio
from jager.server import create_app, is_owner, verify_signature
from jager.store import Store

SECRET = "s3cret"


def build():
    s = Settings(zernio_webhook_secret=SECRET, owner_id="+351 912 345 678", dry_run=True, db_path=":memory:", write_pace_s=0, batch_pause_s=0)
    j = Jager(s, MockZernio(), store=Store(":memory:"), sleep=lambda _x: None)
    return TestClient(create_app(s, j, run_scheduler=False)), j


def post(client, event, secret=SECRET, headers=None):
    body = json.dumps(event).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/webhooks/zernio", content=body, headers={"x-zernio-signature": sig, **(headers or {})})


def msg(eid, text, sender_id="351912345678", direction="incoming"):
    return {"id": eid, "event": "message.received", "message": {"id": "m", "conversationId": "conv1", "platform": "whatsapp",
            "direction": direction, "text": text, "sender": {"id": sender_id}}, "account": {"accountId": "acc1"}}


def test_signature_verification():
    body = b'{"a":1}'
    good = hmac.new(b"k", body, hashlib.sha256).hexdigest()
    assert verify_signature(body, good, "k") and verify_signature(body, "sha256=" + good, "k")
    assert not verify_signature(body, good[:-1] + "0", "k") and not verify_signature(body, None, "k") and not verify_signature(body, good, "")


def test_refuses_to_start_without_secret():
    import pytest

    from jager.config import ConfigError
    with pytest.raises(ConfigError):
        create_app(Settings(zernio_webhook_secret=""), Jager.demo(), run_scheduler=False)


def test_bad_signature_is_401_and_logged():
    c, j = build()
    assert post(c, msg("e1", "hi"), secret="wrong").status_code == 401
    assert any(r["status"] == "bad-signature" for r in j.store.export_log())


def test_owner_gets_a_reply_and_chat_route_is_learned():
    c, j = build()
    assert post(c, msg("e2", "help")).json() == {"ok": True}
    sent = j.api.sent
    assert sent and sent[0][:2] == ("acc1", "conv1") and "Jager" in sent[0][2]
    assert j.store.get("chat") == {"account_id": "acc1", "conversation_id": "conv1"}


def test_duplicate_delivery_is_processed_once():
    c, j = build()
    post(c, msg("e3", "help"))
    n = len(j.api.sent)
    assert post(c, msg("e3", "help")).json().get("duplicate") is True and len(j.api.sent) == n


def test_strangers_are_ignored():
    c, j = build()
    post(c, msg("e4", "delete everything", sender_id="999"))
    assert j.api.sent == [] and any(r["status"] == "ignored-stranger" for r in j.store.export_log())


def test_own_echo_is_ignored():
    c, j = build()
    post(c, msg("e5", "help", direction="outgoing"))
    assert j.api.sent == []


def test_oversized_body_rejected():
    c, _ = build()
    assert c.post("/webhooks/zernio", content=b"x" * 1_100_000, headers={"x-zernio-signature": "x"}).status_code == 413


def test_health_and_no_docs_exposed():
    c, _ = build()
    assert c.get("/health").json()["ok"] is True
    assert c.get("/docs").status_code == 404 and c.get("/openapi.json").status_code == 404


def test_owner_matching_is_forgiving_but_fail_closed():
    assert is_owner({"phoneNumber": "+351912345678"}, "351 912 345 678")
    assert is_owner({"username": "Paul"}, "@paul")
    assert not is_owner({"id": "1"}, "")              # no owner configured: nobody is the owner
    assert not is_owner({}, "123")
