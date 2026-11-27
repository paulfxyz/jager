# Build Jager: multi-agent build prompt

Paste this whole file into your orchestrator agent (Claude Code, Codex, Perplexity Computer or similar). It will plan the work, spawn specialist agents, and ship an MIT-licensed open-source app called Jager.

---

## 0. Mission

Build **Jager** (pronounced "Ya-guerr", jager.social): a free, open-source (MIT) buddy that lives in your WhatsApp or Telegram, tells you what you posted, deals with your public comments, and runs cleanup "sprints" on your social accounts.

Tagline: **Post drunk. Wake up clean.**

Jager is a small server the user runs themselves. It has no hosted backend, no accounts, no login and no signup, and it stores nothing on anyone else's servers. The user brings three keys:

1. **Zernio API key**. Zernio connects the user's social accounts (X, Instagram, Facebook, LinkedIn, TikTok, YouTube, Threads, Bluesky and anything else Zernio supports) and provides the WhatsApp number or Telegram bot used as the chat channel.
2. **OpenRouter API key**. This is the brain: understands messages, summarises, drafts replies, classifies comments.
3. **Runware API key (optional)**. Image jobs such as alt text, image checks, or a picture to go with a reply.

Everything else is code in one repository.

## 1. Ground rules for every agent

- **Read the docs before coding against them. Never guess an endpoint, field or webhook shape.**
  - Zernio quickstart: https://docs.zernio.com/quickstart.mdx
  - Connecting accounts: https://docs.zernio.com/guides/connecting-accounts.mdx
  - Telegram: https://docs.zernio.com/llms/platforms/telegram.txt
  - Zernio also publishes per-platform docs under https://docs.zernio.com/llms/platforms/. Fetch the ones you need.
  - OpenRouter: https://openrouter.ai/docs
  - Runware: https://docs.runware.ai
- If the docs do not support something (for example deleting a post on a given platform), **do not fake it**. Return a clear "not supported on <platform>" result and surface it to the user in chat.
- Licence is **MIT**, copyright "Enki Ltd". Every dependency must be MIT, BSD, Apache-2.0 or ISC compatible.
- **Never log or commit secrets.** Keys come from environment variables only. Ship `.env.example`, never `.env`.
- Safety first (see section 5). Destructive actions need explicit confirmation.
- Keep it small. Target under 3,000 lines of application code, few dependencies, one `docker compose up -d` to run.
- Voice: funny, warm, slightly Gen Z, never cruel. Jager can tease the user. Jager never shames anyone.
- No emojis in code, docs or commit messages. Jager's chat replies may use them sparingly.
- Commit after each merged work package. End every commit message with the trailer `Co-authored-by: Perplexity <noreply@perplexity.ai>`.

## 2. Recommended stack (change only with a written reason)

- **Language:** TypeScript on Node 22, or Python 3.12. Pick one, justify it in `docs/DECISIONS.md`, and stick to it.
- **Web layer:** one small HTTP server (Fastify or FastAPI) exposing `POST /webhooks/zernio` and `GET /health`.
- **Storage:** SQLite (single file `data/jager.db`). No external database.
- **Scheduler:** in-process cron (node-cron or APScheduler) for weekly reminders and sprint timers.
- **Packaging:** Dockerfile and `docker-compose.yml`. A non-root user. A mounted `./data` volume.
- **Tests:** Vitest or pytest, plus a mock Zernio server so the whole app runs offline.

## 3. Architecture

```
You (WhatsApp / Telegram)
        |
     Zernio  <---- your connected social accounts
        |  webhook
   Jager server (yours)
     |- Channel layer   : inbound/outbound chat via Zernio
     |- Brain           : OpenRouter (intent, summaries, drafts)
     |- Social layer    : list posts, comments; delete, hide, reply via Zernio
     |- Sprint engine   : queue of proposed actions, confirm, execute, report
     |- Scheduler       : weekly reminder, sprint timers
     |- Store           : SQLite (settings, sprint state, action log)
        |
   OpenRouter / Runware (optional images)
```

Modules (one folder each, small public interfaces):

| Module | Responsibility |
|---|---|
| `channel/` | Receive chat messages from Zernio webhooks, verify the signature, send replies, quick-reply buttons where the channel supports them |
| `social/` | Thin typed wrapper over the Zernio API: accounts, recent posts, comments, delete, hide, reply. Normalises platform differences |
| `brain/` | OpenRouter client, prompts, JSON-schema tool calls, model fallback chain, cost guard |
| `intents/` | Turns a chat message into a structured intent (see section 4) |
| `sprints/` | Sprint state machine and the confirmation protocol |
| `scheduler/` | Weekly reminder, "sprint is running" nudges, quiet hours |
| `store/` | SQLite schema and migrations, action log (append-only) |
| `i18n/` | Message catalogue, English and French first, easy to add languages |
| `cli/` | `jager doctor`, `jager connect-check`, `jager export-log` |

## 4. Features (v1 scope)

### 4.1 Chat commands (natural language, any phrasing)

- **Recap:** "what did I post this week?" returns a numbered list with platform, text snippet, date.
- **Delete:** "delete 2 and 4", "delete everything from tonight", "delete all of it". Always confirmed, see section 5.
- **Keep:** "keep 3" marks a post as protected so no sprint proposes it again.
- **Timer:** "delete everything I post tonight, an hour after I post it". Creates an auto-delete rule with a window, scope (platforms, time range) and an expiry date.
- **Comments:** "what's new in my comments?" Jager groups comments into: needs a reply, questions, praise, spam, trolls. He serves them one at a time with a suggested action: send draft, edit, hide, delete, skip.
- **Reply drafting:** Jager drafts a reply in the user's voice (learned from the user's last 20 own posts, kept as a short style note, never sent anywhere except the chosen OpenRouter model).
- **Status and help:** "status", "help", "pause", "resume".

### 4.2 Weekly reminder

Every week at a user-chosen day and time (default Sunday 18:00, user timezone), Jager messages:
what you posted, how many new comments are waiting, and offers: "Start a sprint?" Reply `yes`, `later` or `skip this week`. Respect quiet hours.

### 4.3 Sprints

A sprint is a short, focused session. Types:

- **Comment sprint:** goes through unanswered comments one by one.
- **Cleanup sprint:** goes through old posts (older than N days, or matching a keyword) and proposes keep or delete.
- **Night sprint:** triggered by the user ("I'm going out"): auto-delete rule for the night, then a morning recap.

Sprint state machine: `proposed -> confirmed -> running -> paused -> done | cancelled`. The user can say "stop" at any time. A sprint always ends with a summary: what was deleted, hidden, replied to, kept.

### 4.4 Languages

English and French at launch. All user-facing strings live in `i18n/` catalogues. Adding a language means adding one file. The intent parser must accept messages in the user's language.

### 4.5 Setup experience

- `jager doctor` checks: keys present, Zernio reachable, accounts connected, chat channel working, webhook URL reachable, OpenRouter model responding. Prints plain-language fixes.
- First message flow: Jager introduces himself, lists connected accounts, asks for timezone, reminder day and quiet hours.

## 5. Safety rules (non-negotiable, add tests for each)

1. **Never delete, hide or reply without an explicit user confirmation** in the same chat, except for auto-delete rules the user created themselves with a clear scope and expiry.
2. **Confirmation protocol:** Jager restates exactly what will happen ("Delete 2 posts (2, 4) for good? Reply YES"). Only the confirmation word in the right language, from the right user, within 10 minutes, counts. Anything else cancels.
3. **Only the owner can command Jager.** The chat sender must match the configured owner ID. Everyone else is ignored and logged.
4. **Webhook signature verification** on every inbound request. Reject and log otherwise.
5. **Dry run mode** (`JAGER_DRY_RUN=true`): everything works except the final API call, which is logged instead.
6. **Action log:** every proposed, confirmed, executed and failed action is written to an append-only table with timestamps. `jager export-log` dumps it as JSON.
7. **Rate limits and backoff** for every Zernio and OpenRouter call. Bulk deletes run in small batches with pauses.
8. **Prompt injection defence:** comment text and post text are untrusted data. They are passed to the model inside clearly delimited blocks, the model has no tools that act without the confirmation layer, and no comment can change instructions, owner or settings.
9. **Cost guard:** a daily token or spend ceiling (`JAGER_DAILY_BUDGET_USD`), default 0.50. When reached, Jager says so and falls back to basic commands.
10. **Privacy:** post and comment content is sent only to the chosen OpenRouter model and Runware if images are enabled. Nothing else. No analytics, no telemetry.

## 6. Configuration (`.env.example`)

```
ZERNIO_API_KEY=
ZERNIO_WEBHOOK_SECRET=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=            # a cheap default plus JAGER_FALLBACK_MODELS (comma-separated)
RUNWARE_API_KEY=             # optional
JAGER_OWNER_ID=              # your WhatsApp number or Telegram user id
JAGER_TIMEZONE=Europe/Lisbon
JAGER_LANGUAGE=en
JAGER_DRY_RUN=true           # ships on; user turns it off deliberately
JAGER_DAILY_BUDGET_USD=0.50
PORT=8080
```

Default model choice: pick a low-cost model on OpenRouter that supports JSON output, and a second fallback from a different provider. Document the choice and expected cost per week in `docs/COSTS.md`. Honour any model the user sets.

## 7. Agent team

The orchestrator creates a plan, then spawns these agents. Agents work in separate git branches or worktrees and message the orchestrator with a short result when done. Each agent owns specific files and does not edit anyone else's.

| # | Agent | Owns | Deliverable |
|---|---|---|---|
| 1 | **Architect** | `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, repo skeleton, tooling | Skeleton that builds, lints and tests in CI. Interfaces for every module (types only). Runs first, alone. |
| 2 | **Zernio Integrator** | `social/`, `channel/` | Typed Zernio client, webhook handler with signature check, capability matrix per platform (what can be listed, deleted, hidden, replied to). A mock Zernio server for tests. |
| 3 | **Brain Engineer** | `brain/`, `intents/` | OpenRouter client with fallback chain and budget guard, intent schema, prompt files in `prompts/`, injection-hardened templates, an eval set of at least 60 multilingual messages with expected intents. |
| 4 | **Sprint Engineer** | `sprints/`, `scheduler/`, `store/` | State machine, confirmation protocol, weekly reminder, auto-delete rules, SQLite schema with migrations, action log. |
| 5 | **Voice and i18n Writer** | `i18n/`, `docs/VOICE.md` | EN and FR catalogues, Jager's personality guide with 20 example replies, error messages, onboarding script. Idiomatic, no mixed-language strings. |
| 6 | **QA and Safety Auditor** | `tests/`, `docs/SAFETY.md` | Tests for all ten safety rules, end-to-end scripted chats against the mock, dry-run verification, a red-team pass using hostile comments. Can block a release. |
| 7 | **DevOps and Docs** | `Dockerfile`, `docker-compose.yml`, `README.md`, `docs/SETUP.md`, CI | One-command run, a guide for Zernio, WhatsApp or Telegram, OpenRouter and Runware setup with the exact steps, a troubleshooting section, release workflow, GitHub issue templates. |
| 8 | **Reviewer** | read-only | Reviews every merge for scope creep, secrets, licence issues and unsupported claims. Writes `CHANGELOG.md`. |

Order of work:

1. Architect (alone).
2. Agents 2, 3, 4, 5 in parallel against the interfaces.
3. Agent 6 starts as soon as there is something to test and keeps going to the end.
4. Agent 7 starts once the app runs end to end.
5. Reviewer gates every merge.
6. Orchestrator integrates, runs the full test suite and `jager doctor` against the mock, then tags `v0.1.0`.

## 8. Definition of done

- `docker compose up -d` starts the app with only `.env` filled in.
- A scripted chat against the mock Zernio passes: recap, delete with confirmation, wrong confirmation cancels, comment sprint, weekly reminder, auto-delete rule, pause and resume.
- Every safety rule has a failing-then-passing test.
- Dry run is the default and is documented loudly.
- Capability matrix shows, per platform, what Jager can really do. Unsupported actions say so in chat.
- README explains in plain language: what Jager is, the three keys, a five-minute setup, what he never does, and the cost per week.
- Licence file is MIT, copyright Enki Ltd. Footer in docs: "Jager is a sister project of Iris and Digital Spot, by Enki Ltd."
- No secrets in git history. A secret scan passes.
- Repository is private until the orchestrator reports the checklist above as green, then it waits for the owner to make it public.

## 9. Repository layout

```
jager/
  README.md  LICENSE  CHANGELOG.md  SECURITY.md  CONTRIBUTING.md
  .env.example  Dockerfile  docker-compose.yml
  docs/        ARCHITECTURE.md DECISIONS.md SAFETY.md SETUP.md COSTS.md VOICE.md
  prompts/     intents.md  reply-draft.md  classify-comment.md  recap.md
  src/         channel/ social/ brain/ intents/ sprints/ scheduler/ store/ i18n/ cli/
  tests/       unit/ e2e/ evals/ mocks/
  .github/     workflows/ISSUE_TEMPLATE/
```

## 10. Reporting back

Each agent finishes with a message of at most 10 lines: what was built, what was tested, what is missing, any doc claim it could not verify. The orchestrator ends with one summary for the owner: what works, what Zernio cannot do per platform, the estimated weekly cost, open questions, and the exact commands to try it.

Start now: read the Zernio docs, then run the Architect.
