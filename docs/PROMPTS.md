# Build Jager with your agents (the prompt kit)

Jager is designed to be recreated, extended and understood by AI agents. Everything needed lives in [`prompts/`](../prompts). Pick the prompt that matches what you want, paste it into **Claude Code, Codex, Perplexity Computer, Cursor** or any agent that can read a repo or a URL, and go.

| File | Use it when | Prompts needed |
|---|---|---|
| [`prompts/01-understand-and-run.md`](../prompts/01-understand-and-run.md) | You want an agent to read the repo, explain it and get it running | 1 |
| [`prompts/02-add-a-language.md`](../prompts/02-add-a-language.md) | You want Jager in another language | 1 |
| [`prompts/03-add-a-command.md`](../prompts/03-add-a-command.md) | You want a new chat command or sprint, safely | 1 |
| [`prompts/04-adapt-to-my-stack.md`](../prompts/04-adapt-to-my-stack.md) | You want Jager inside your own app (Django, n8n, a Discord bot, a cron job...) | 1 to 2 |
| [`prompts/MASTER.md`](../prompts/MASTER.md) | You want an orchestrator and a team of agents to rebuild the **whole product** (app, library, website) from nothing | 1 big one |

## The 3-prompt path from zero to running

1. **Understand.** Paste `01-understand-and-run.md`. The agent reads the repo and tells you what it found.
2. **Configure.** The same prompt walks you through the three keys, asks you for them (never paste keys into a chat you do not trust; use your agent's secret store or `.env` locally) and runs `jager doctor`.
3. **Extend.** Paste `03-add-a-command.md` or `04-adapt-to-my-stack.md` and tell the agent what you want.

## Tips that make agents behave

- Point the agent at the repo URL and let it read `docs/LEARN.md` first. That file was written for humans and works great for models too.
- Tell it the safety rules are non-negotiable (all prompts do).
- Ask it to run `pytest -q` after every change. The suite takes under a second.
- If it wants to touch `capabilities.py`, make it cite the Zernio doc URL for each change.
