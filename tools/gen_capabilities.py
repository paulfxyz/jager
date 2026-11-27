"""Regenerate docs/CAPABILITIES.md from src/jager/capabilities.py.

The test suite fails if the doc and the code disagree, so the documentation can never quietly lie.
    python tools/gen_capabilities.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from jager import capabilities as cap  # noqa: E402

HEADER = """# What Jager can do on each network

> Generated from `src/jager/capabilities.py` by `tools/gen_capabilities.py`. Do not edit by hand:
> a test fails if this file and the code disagree.

Jager talks to social networks through [Zernio](https://zernio.com). Zernio gives one API, but each
network decides what an app may do. Jager keeps this table and checks it **before** acting, so he never
promises something the network will refuse. If an action is impossible, he says so in chat.

Every cell was read from the Zernio documentation on 2026-11-27:
[unpublish post](https://docs.zernio.com/posts/unpublish-post.mdx),
[comments](https://docs.zernio.com/products/comments.mdx),
[delete comment](https://docs.zernio.com/comments/delete-inbox-comment.mdx),
[hide comment](https://docs.zernio.com/comments/hide-inbox-comment.mdx).

| Network | Delete posts | Read comments | Reply | Hide | Delete comments | Notes |
|---|:-:|:-:|:-:|:-:|:-:|---|
"""


def render() -> str:
    mark = lambda b: "yes" if b else "no"  # noqa: E731
    rows = [f"| {r['name']} | {mark(r['delete_post'])} | {mark(r['read_comments'])} | {mark(r['reply_comment'])} | "
            f"{mark(r['hide_comment'])} | {mark(r['delete_comment'])} | {r['note']} |" for r in cap.table()]
    return HEADER + "\n".join(rows) + """

## Good to know

- **Deleting a post uses Zernio's unpublish endpoint**, which takes the Zernio post id. Posts that were
  published outside Zernio may not be deletable through it. Jager reports the failure instead of guessing.
- **YouTube deletions are permanent.** Jager still asks YES first, like always.
- **X bills every read** through your X API usage. Jager keeps reads small (one page, newest first) and
  caches for 30 seconds.
- **TikTok** comment features need an account connected through the TikTok for Business app.
- Comment webhooks are real time on Instagram, Facebook, Threads and TikTok. YouTube, LinkedIn, Bluesky and
  Reddit are polled by Zernio (minutes of delay). X sends no comment webhook.
- When Zernio changes something, edit `capabilities.py`, run `python tools/gen_capabilities.py`, run the tests.
"""


if __name__ == "__main__":
    pathlib.Path(__file__).resolve().parents[1].joinpath("docs/CAPABILITIES.md").write_text(render())
    print("docs/CAPABILITIES.md written")
