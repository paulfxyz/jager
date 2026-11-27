"""MockZernio: a pocket-sized fake of Zernio, for tests and the offline demo.

It implements the same ``SocialAPI`` methods as the real client, keeps state in
memory and obeys the real capability matrix: ask it to delete an Instagram post
and it refuses, exactly like the real thing. This is what lets you try Jager
without keys, and lets the test suite run offline in under a second.

The sample content is, ahem, based on a true story.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .capabilities import can, why_not
from .models import Account, Comment, Post
from .zernio import Unsupported


class MockZernio:
    def __init__(self, now: datetime | None = None):
        self.now = now or datetime.now(UTC)
        self.sent: list[tuple[str, str, str]] = []      # (account, conversation, text) chat messages
        self.calls: list[tuple] = []                    # every write, for assertions in tests
        h = lambda n: self.now - timedelta(hours=n)     # noqa: E731  "n hours ago"
        self._accounts = [Account("a-x", "twitter", "@paul"), Account("a-ig", "instagram", "@paul.ig"),
                          Account("a-li", "linkedin", "paul-fleury"), Account("a-th", "threads", "@paul"),
                          Account("a-bs", "bluesky", "paul.bsky.social")]
        self._posts: list[Post] = [
            Post("p1", "a-x", "twitter", "pineapple on pizza is a personality test and I failed on purpose", h(5)),
            Post("p2", "a-li", "linkedin", "Thrilled to announce I am in a kebab shop and have never been more aligned.", h(30)),
            Post("p3", "a-ig", "instagram", "my dog in a tiny hat. nothing to add.", h(52)),
            Post("p4", "a-th", "threads", "reply to my boss: bro we do NOT have synergy", h(75)),
            Post("p5", "a-bs", "bluesky", "all my exes are going to see this and I am fine with that", h(100)),
            Post("p6", "a-x", "twitter", "quarterly update: still alive", h(24 * 20)),   # too old for the weekly recap
        ]
        self._comments: dict[str, list[Comment]] = {
            "p1": [Comment("c1", "p1", "a-x", "twitter", "this is the worst take of 2026", "@pizzapurist", h(4)),
                   Comment("c2", "p1", "a-x", "twitter", "BUY CRYPTO NOW www.totally-legit.example", "@botbotbot", h(3))],
            "p2": [Comment("c3", "p2", "a-li", "linkedin", "Could you share more about the kebab synergy?", "Dana", h(20)),
                   Comment("c4", "p2", "a-li", "linkedin", "Congrats!", "Marc", h(18))],
            "p3": [Comment("c5", "p3", "a-ig", "instagram", "the hat is serious business", "@dogfan", h(40))],
        }

    # ---- reading -----------------------------------------------------------
    def accounts(self) -> list[Account]:
        return list(self._accounts)

    def posts(self, account: Account, since: datetime, limit: int = 50) -> list[Post]:
        rows = [p for p in self._posts if p.account_id == account.id and p.created >= since]
        return sorted(rows, key=lambda p: p.created, reverse=True)[:limit]

    def commented_posts(self, since: datetime, limit: int = 20) -> list[dict]:
        out = []
        for pid, cs in self._comments.items():
            post = next((p for p in self._posts if p.id == pid), None)
            if post and cs and post.created >= since:
                out.append({"id": pid, "account_id": post.account_id, "platform": post.platform,
                            "text": post.text, "count": len(cs)})
        return out[:limit]

    def comments(self, post_id: str, account_id: str, platform: str, limit: int = 50) -> list[Comment]:
        if not can(platform, "read_comments"):
            raise Unsupported(why_not(platform, "read_comments"))
        return [c for c in self._comments.get(post_id, []) if not c.is_hidden][:limit]

    # ---- writing (all obey the capability matrix) --------------------------------
    def delete_post(self, post: Post) -> None:
        if not can(post.platform, "delete_post"):
            raise Unsupported(why_not(post.platform, "delete_post"))
        self.calls.append(("delete_post", post.id))
        self._posts = [p for p in self._posts if p.id != post.id]

    def reply(self, comment: Comment, message: str) -> None:
        if not can(comment.platform, "reply_comment"):
            raise Unsupported(why_not(comment.platform, "reply_comment"))
        self.calls.append(("reply", comment.id, message))

    def hide_comment(self, comment: Comment) -> None:
        if not can(comment.platform, "hide_comment"):
            raise Unsupported(why_not(comment.platform, "hide_comment"))
        self.calls.append(("hide", comment.id))
        comment.is_hidden = True

    def delete_comment(self, comment: Comment) -> None:
        if not can(comment.platform, "delete_comment"):
            raise Unsupported(why_not(comment.platform, "delete_comment"))
        self.calls.append(("delete_comment", comment.id))
        self._comments[comment.post_id] = [c for c in self._comments.get(comment.post_id, []) if c.id != comment.id]

    def send_message(self, account_id: str, conversation_id: str, text: str) -> None:
        self.sent.append((account_id, conversation_id, text))

    # ---- test helpers ----------------------------------------------------------
    def add_post(self, post: Post) -> None:
        self._posts.append(post)
