# Prompt 4: adapt Jager to my own stack

---

Repo: https://github.com/paulfxyz/jager (MIT). My stack: **<DESCRIBE: e.g. a Django app, an n8n workflow, a Discord bot, a serverless cron, a Node service>**.

Goal: **<WHAT I WANT, e.g. send the weekly recap to Slack and let me approve deletes there>**.

1. Read `docs/LEARN.md` and `docs/ARCHITECTURE.md`. Jager exposes `Jager.from_env()`, `weekly_recap()`, `sprint(kind)` and `handle(text)`; the chat transport is just a `send(text)` callable passed to the constructor, and the social backend is anything implementing the `SocialAPI` protocol in `zernio.py`.
2. Propose the thinnest integration: which of those seams do we use? Prefer importing Jager as a library over forking it. Show me the plan in 10 lines before coding.
3. If my stack is not Python, propose either running Jager as its own service and talking to it through the webhook, or a port, and tell me honestly which is less work.
4. Implement it with tests. Keep the safety rules: explicit confirmation before destructive actions (the owner's YES must come from a human in my channel), dry run by default, capability checks, append-only logging.
5. Give me run instructions and the list of environment variables.
