# Prompt 1: understand and run Jager

Copy everything below the line into your agent.

---

You are helping me run **Jager**, a free open-source (MIT) buddy that lives in my WhatsApp or Telegram and helps me clean up my social media posts and comments. Repo: https://github.com/paulfxyz/jager

Do this in order, and stop to ask me whenever something needs a decision or a secret:

1. **Read** `README.md`, `docs/LEARN.md`, `docs/INSTALL.md` and `docs/SAFETY.md`. Then explain Jager to me in 10 lines: what it does, the three keys, how a message travels from my phone to a delete, and the safety rules.
2. **Check my machine**: Python 3.11+ or Docker available? If not, tell me the simplest way to get one.
3. **Install** following `docs/INSTALL.md` (Docker preferred). Do not invent steps.
4. **Configure** `.env` from `.env.example`. Ask me for: my Zernio API key, my owner id (phone or Telegram id) and, optionally, an OpenRouter key. Generate `ZERNIO_WEBHOOK_SECRET` yourself with a secure random generator. Never print my keys back, never commit `.env`, never put keys on the command line where they would end up in shell history if you can avoid it.
5. **Keep `JAGER_DRY_RUN=true`.** Do not turn it off unless I explicitly tell you to in this conversation.
6. **Run** `jager doctor` and fix every FAIL it reports, explaining each one in plain words.
7. **Expose** the webhook (Cloudflare Tunnel is simplest) and register it with `jager webhook-setup`.
8. **Verify** by asking me to send "help" to Jager in my chat app, then run `jager export-log` and show me what happened.
9. Finish with a short checklist of what is live and what I should do next (watch him in dry run for a day, then flip the flag).

Rules for you: follow the docs rather than guessing; the confirmation-before-delete behaviour and the capability matrix are non-negotiable; if the docs and reality disagree, tell me instead of working around it.
