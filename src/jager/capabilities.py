"""What can Jager actually do on each network? (The honest matrix.)

Social networks are like bouncers: each one has its own rules about who gets in
and what you may do inside. Zernio gives us one API, but it cannot make a
network do what the network refuses to do. So instead of pretending, Jager
keeps this table and consults it BEFORE acting. If an action is impossible, he
says so in chat ("Instagram does not let me delete posts, sorry, you will have
to do it yourself") rather than failing silently at 2 AM.

Every cell below was read from the Zernio docs on 2026-11-27. When Zernio
changes something, change this file, run the tests, and bump the version.
Sources:
  * Unpublish (delete a published post):
      https://docs.zernio.com/posts/unpublish-post.mdx
  * Comments (read, reply, hide, delete):
      https://docs.zernio.com/products/comments.mdx
      https://docs.zernio.com/comments/delete-inbox-comment.mdx
      https://docs.zernio.com/comments/hide-inbox-comment.mdx
  * Listing live posts:
      https://docs.zernio.com/accounts/get-account-posts.mdx
"""

from __future__ import annotations

from dataclasses import dataclass

# Zernio's platform slugs, in the order we like to show them off.
PLATFORMS = [
    "twitter", "instagram", "facebook", "linkedin", "tiktok", "youtube",
    "threads", "bluesky", "pinterest", "reddit", "googlebusiness", "snapchat",
]

# Pretty names for humans (X will always be Twitter in our hearts).
NAMES = {
    "twitter": "X", "instagram": "Instagram", "facebook": "Facebook",
    "linkedin": "LinkedIn", "tiktok": "TikTok", "youtube": "YouTube",
    "threads": "Threads", "bluesky": "Bluesky", "pinterest": "Pinterest",
    "reddit": "Reddit", "googlebusiness": "Google Business", "snapchat": "Snapchat",
}

# The five things Jager might want to do.
ACTIONS = ("delete_post", "read_comments", "reply_comment", "hide_comment", "delete_comment")


@dataclass(frozen=True)
class Cap:
    """One platform's powers, plus a human note when there is a catch."""
    delete_post: bool = False
    read_comments: bool = False
    reply_comment: bool = False
    hide_comment: bool = False
    delete_comment: bool = False
    note: str = ""


_COMMENTS = {"read_comments": True, "reply_comment": True}

MATRIX: dict[str, Cap] = {
    # X: can delete its own posts; hides only replies in your own threads; may delete only your own comments.
    "twitter": Cap(delete_post=True, **_COMMENTS, hide_comment=True, delete_comment=True,
                   note="X bills every read. Hiding works on replies in your own threads. No real-time comment webhook, so Jager polls."),
    # Instagram: Meta does not let anyone unpublish a post via API. Comments are fully moderatable.
    "instagram": Cap(delete_post=False, **_COMMENTS, hide_comment=True, delete_comment=True,
                     note="Instagram does not allow deleting posts through the API. Comments: full moderation."),
    "facebook": Cap(delete_post=True, **_COMMENTS, hide_comment=True, delete_comment=True,
                    note="Pages can delete anyone's comment on their own posts."),
    "linkedin": Cap(delete_post=True, **_COMMENTS, hide_comment=False, delete_comment=True,
                    note="No hiding on LinkedIn. Deleting any comment works on organization pages; personal profiles are more limited."),
    "tiktok": Cap(delete_post=False, **_COMMENTS, hide_comment=True, delete_comment=True,
                  note="Needs an account connected through the TikTok for Business app. Only your own comments can be deleted, hide the rest. Post deletion is not supported. Only the newest page of posts can be listed."),
    "youtube": Cap(delete_post=True, **_COMMENTS, hide_comment=False, delete_comment=True,
                   note="Video deletion is PERMANENT. Other people's comments get rejected (moderation) rather than deleted."),
    "threads": Cap(delete_post=True, **_COMMENTS, hide_comment=True, delete_comment=True,
                   note="Meta refuses deleting other people's replies on Threads: hide them (top-level replies only)."),
    "bluesky": Cap(delete_post=True, **_COMMENTS, hide_comment=False, delete_comment=True,
                   note="You can delete your own comments. No hiding."),
    # The three networks below: Zernio lists them for posting, but comments are not offered.
    "pinterest": Cap(delete_post=True, note="Pins only. No comment moderation through Zernio."),
    "reddit": Cap(delete_post=True, **_COMMENTS, hide_comment=False, delete_comment=True,
                  note="You can delete your own comments. No hiding."),
    "googlebusiness": Cap(delete_post=True, note="Posts only. Reviews exist in Zernio's Inbox API but are not part of Jager v0.1."),
    "snapchat": Cap(delete_post=False, note="Zernio cannot unpublish Snapchat posts, and there are no comments to moderate."),
}

# Platforms where comment.received webhooks do NOT fire in real time (we must poll).
POLLED_COMMENTS = {"twitter", "youtube", "linkedin", "bluesky", "reddit"}
# Platforms that never send comment.received at all.
NO_COMMENT_WEBHOOK = {"twitter", "pinterest", "googlebusiness", "snapchat"}

_HUMAN = {
    "delete_post": "delete posts",
    "read_comments": "read comments",
    "reply_comment": "reply to comments",
    "hide_comment": "hide comments",
    "delete_comment": "delete comments",
}


def can(platform: str, action: str) -> bool:
    """Is ``action`` possible on ``platform``? Unknown platforms: no (be conservative)."""
    if action not in ACTIONS:
        raise ValueError(f"unknown action {action!r}; expected one of {ACTIONS}")
    cap = MATRIX.get(platform)
    return bool(cap and getattr(cap, action))


def why_not(platform: str, action: str) -> str:
    """A human sentence explaining why Jager cannot do ``action`` on ``platform``."""
    name = NAMES.get(platform, platform)
    cap = MATRIX.get(platform)
    if cap is None:
        return f"I do not know {name} yet, so I will not touch it."
    extra = f" ({cap.note})" if cap.note else ""
    return f"{name} does not let me {_HUMAN[action]} through Zernio{extra}."


def table() -> list[dict]:
    """The matrix as plain dicts (used by `jager capabilities` and the docs generator)."""
    rows = []
    for p in PLATFORMS:
        c = MATRIX[p]
        rows.append({"platform": p, "name": NAMES[p], **{a: getattr(c, a) for a in ACTIONS}, "note": c.note})
    return rows
