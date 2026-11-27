"""Example 3: how a Zernio webhook is signed, and how to test your own server by hand.

    jager serve &                      # in another terminal, with ZERNIO_WEBHOOK_SECRET set
    python examples/03_sign_a_test_webhook.py

Zernio signs the RAW request body with HMAC-SHA256 and your secret, and sends the hex digest in
the X-Zernio-Signature header. Jager recomputes it and compares in constant time. If you change a
single byte of the body, or use the wrong secret, you get a 401. Try it.
"""
import hashlib
import hmac
import json
import os
import urllib.request

SECRET = os.environ.get("ZERNIO_WEBHOOK_SECRET", "change-me")
OWNER = os.environ.get("JAGER_OWNER_ID", "351912345678")

event = {
    "id": "evt-demo-1",                      # the dedupe key: send the same id twice and the second is ignored
    "event": "message.received",
    "message": {"id": "m1", "conversationId": "demo-conv", "platform": "telegram", "direction": "incoming",
                "text": "help", "sender": {"id": OWNER}},
    "account": {"accountId": "demo-account"},
}
body = json.dumps(event).encode()
signature = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()

req = urllib.request.Request("http://127.0.0.1:8080/webhooks/zernio", data=body,
                             headers={"Content-Type": "application/json", "X-Zernio-Signature": signature})
with urllib.request.urlopen(req, timeout=5) as r:   # noqa: S310 - local URL on purpose
    print(r.status, r.read().decode())
