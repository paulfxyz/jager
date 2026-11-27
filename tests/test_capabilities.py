"""The capability matrix is a promise. These tests pin it to what the Zernio docs say."""
from jager import capabilities as cap


def test_twelve_platforms():
    assert len(cap.PLATFORMS) == 12 and set(cap.PLATFORMS) == set(cap.MATRIX)


def test_documented_delete_refusals():
    # https://docs.zernio.com/posts/unpublish-post.mdx: "Not supported on Instagram, TikTok, or Snapchat."
    for p in ("instagram", "tiktok", "snapchat"):
        assert not cap.can(p, "delete_post")
    assert cap.can("twitter", "delete_post") and cap.can("youtube", "delete_post")


def test_exactly_nine_platforms_have_comments():
    # https://docs.zernio.com/products/comments.mdx: "across nine social platforms"
    assert sum(cap.can(p, "read_comments") for p in cap.PLATFORMS) == 9


def test_hide_matches_docs():
    hiders = {p for p in cap.PLATFORMS if cap.can(p, "hide_comment")}
    assert hiders == {"instagram", "facebook", "twitter", "threads", "tiktok"}


def test_unknown_platform_is_denied_and_explained():
    assert not cap.can("myspace", "delete_post")
    assert "myspace" in cap.why_not("myspace", "delete_post")


def test_unknown_action_raises():
    import pytest
    with pytest.raises(ValueError):
        cap.can("twitter", "teleport")


def test_capabilities_doc_matches_code():
    """The documentation may never quietly lie: regenerate it with tools/gen_capabilities.py."""
    import pathlib
    import sys
    root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tools"))
    import gen_capabilities
    assert (root / "docs/CAPABILITIES.md").read_text() == gen_capabilities.render()
