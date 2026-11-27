# What Jager can do on each network

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
| X | yes | yes | yes | yes | yes | X bills every read. Hiding works on replies in your own threads. No real-time comment webhook, so Jager polls. |
| Instagram | no | yes | yes | yes | yes | Instagram does not allow deleting posts through the API. Comments: full moderation. |
| Facebook | yes | yes | yes | yes | yes | Pages can delete anyone's comment on their own posts. |
| LinkedIn | yes | yes | yes | no | yes | No hiding on LinkedIn. Deleting any comment works on organization pages; personal profiles are more limited. |
| TikTok | no | yes | yes | yes | yes | Needs an account connected through the TikTok for Business app. Only your own comments can be deleted, hide the rest. Post deletion is not supported. Only the newest page of posts can be listed. |
| YouTube | yes | yes | yes | no | yes | Video deletion is PERMANENT. Other people's comments get rejected (moderation) rather than deleted. |
| Threads | yes | yes | yes | yes | yes | Meta refuses deleting other people's replies on Threads: hide them (top-level replies only). |
| Bluesky | yes | yes | yes | no | yes | You can delete your own comments. No hiding. |
| Pinterest | yes | no | no | no | no | Pins only. No comment moderation through Zernio. |
| Reddit | yes | yes | yes | no | yes | You can delete your own comments. No hiding. |
| Google Business | yes | no | no | no | no | Posts only. Reviews exist in Zernio's Inbox API but are not part of Jager v0.1. |
| Snapchat | no | no | no | no | no | Zernio cannot unpublish Snapchat posts, and there are no comments to moderate. |

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
