"""The HTTP client: retries, idempotency, caching, tolerant parsing. No network: httpx.MockTransport plays Zernio."""
import json
from datetime import UTC, datetime

import httpx
import pytest

from jager.models import Comment, Post
from jager.zernio import Unsupported, ZernioClient, ZernioError


def client(handler, **kw):
    return ZernioClient("sk_test", transport=httpx.MockTransport(handler), sleep=lambda s: None, **kw)


def test_auth_header_and_account_parsing():
    seen = {}

    def h(req):
        seen["auth"] = req.headers["authorization"]
        return httpx.Response(200, json={"accounts": [{"_id": "a1", "platform": "twitter", "username": "paul"}, {"junk": 1}]})
    accts = client(h).accounts()
    assert seen["auth"] == "Bearer sk_test" and [(a.id, a.platform) for a in accts] == [("a1", "twitter")]


def test_retries_on_429_and_5xx_then_succeeds():
    calls = {"n": 0}

    def h(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "1"}, json={"error": "slow down"})
        if calls["n"] == 2:
            return httpx.Response(503)
        return httpx.Response(200, json={"accounts": []})
    assert client(h).accounts() == [] and calls["n"] == 3


def test_does_not_retry_client_errors():
    calls = {"n": 0}

    def h(req):
        calls["n"] += 1
        return httpx.Response(400, json={"error": "nope", "code": "bad"})
    with pytest.raises(ZernioError):
        client(h).accounts()
    assert calls["n"] == 1                                         # a wrong request does not get righter by repeating it


def test_gives_up_after_max_retries():
    with pytest.raises(ZernioError):
        client(lambda r: httpx.Response(500), max_retries=2).accounts()


def test_writes_carry_idempotency_key_and_gets_do_not():
    keys = []

    def h(req):
        keys.append(req.headers.get("idempotency-key"))
        return httpx.Response(200, json={"success": True})
    c = client(h)
    c.accounts()
    c.delete_post(Post("p1", "a1", "twitter", "x", datetime.now(UTC)))
    assert keys[0] is None and keys[1]


def test_retry_reuses_the_same_idempotency_key():
    keys = []

    def h(req):
        keys.append(req.headers["idempotency-key"])
        return httpx.Response(503) if len(keys) == 1 else httpx.Response(200, json={})
    client(h).send_message("a", "c", "hi")
    assert len(keys) == 2 and keys[0] == keys[1]                    # a retry can never double-send


def test_get_cache_and_write_invalidation():
    n = {"c": 0}

    def h(req):
        n["c"] += 1
        return httpx.Response(200, json={"accounts": []})
    c = client(h)
    c.accounts()
    c.accounts()
    assert n["c"] == 1                                              # second call served from cache
    c.send_message("a", "c", "x")
    c.accounts()
    assert n["c"] == 3                                              # write cleared the cache


def test_platform_limitation_becomes_unsupported():
    def h(req):
        return httpx.Response(400, json={"error": "TikTok developer apps are not supported", "code": "PLATFORM_LIMITATION"})
    with pytest.raises(Unsupported):
        client(h).comments("p", "a", "tiktok")


def test_unpublish_request_shape():
    seen = {}

    def h(req):
        seen.update(path=req.url.path, body=json.loads(req.content))
        return httpx.Response(200, json={"success": True})
    client(h).delete_post(Post("p9", "a1", "bluesky", "x", datetime.now(UTC)))
    assert seen["path"].endswith("/posts/p9/unpublish") and seen["body"] == {"platform": "bluesky", "accountId": "a1"}


def test_posts_stops_at_the_window_edge_and_survives_weird_rows():
    old = "2020-01-01T00:00:00Z"
    new = datetime.now(UTC).isoformat()

    def h(req):
        return httpx.Response(200, json={"posts": [{"id": "n", "message": "hi", "publishedAt": new}, {"weird": True},
                                                    {"id": "o", "message": "old", "publishedAt": old}],
                                         "pagination": {"hasMore": True, "nextCursor": "c"}})
    from jager.models import Account
    got = client(h).posts(Account("a1", "twitter"), datetime(2024, 1, 1, tzinfo=UTC))
    assert [p.id for p in got] == ["n"]


def test_comment_delete_uses_query_params():
    seen = {}

    def h(req):
        seen.update(method=req.method, q=dict(req.url.params))
        return httpx.Response(200, json={})
    client(h).delete_comment(Comment("c1", "p1", "a1", "facebook", "t"))
    assert seen["method"] == "DELETE" and seen["q"] == {"accountId": "a1", "commentId": "c1"}
