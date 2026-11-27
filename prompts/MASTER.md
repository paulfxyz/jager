# Jager: master build prompt (product + website)

Give this file to an orchestrator agent (Claude Code, Codex, Perplexity Computer or similar). It rebuilds the whole of Jager from nothing: the open-source app, the Python library, the landing site in English and French, and the deployment. Work in the order of section 12.

---

## 1. What Jager is

**Jager** (pronounced "Ya-guerr", a pun on Jägermeister) is a free, open-source (MIT) buddy that lives in your WhatsApp or Telegram. It tells you what you posted, deals with the public comments under your posts, and runs short "sprints" that clean up after you.

- Tagline: **Post drunk. Wake up clean.**
- Home: https://jager.social. Sister project of Iris (https://iris.online) and Digital Spot (https://digital.spot).
- Operator and copyright holder: **Enki Ltd**, company number 2067348138, 14 Antim I Street, fl. 1 & 2, Sofia, Bulgaria, contact ask@jager.social.
- Licence: MIT. There is no signup, no login, no pricing, no hosted backend and no "coming soon". The user runs Jager themselves.
- Every call to action points to the GitHub profile https://github.com/paulfxyz (the repo link is a placeholder until the repo is public).
- Launch: Product Hunt on **Thursday 3 December 2026** (Product Hunt days start at 00:01 Pacific, which is 08:01 UTC). Product Hunt links go to https://www.producthunt.com until a launch page exists.

The user brings three keys:

1. **Zernio API key.** Zernio connects the social accounts and provides the WhatsApp number or Telegram bot used as the chat channel.
2. **OpenRouter API key.** The brain: understands messages, summarises, drafts replies, classifies comments.
3. **Runware API key (optional).** Image jobs such as alt text, image checks, a picture to go with a reply.

Three ways to run it, all MIT:

1. **Clone and run:** `git clone`, fill `.env`, `docker compose up -d`.
2. **Import in Python:** use Jager as a library inside your own app, bot or cron job.
3. **Prompt your agents:** a Markdown build prompt (this family of files) that briefs a team of agents to build Jager on your stack.

## 2. Ground rules for every agent

- Read the docs before coding against them. Never guess an endpoint, field or webhook shape.
  - Zernio: https://docs.zernio.com/llms.txt, https://docs.zernio.com/quickstart.mdx, https://docs.zernio.com/guides/connecting-accounts.mdx, https://docs.zernio.com/llms/platforms/telegram.txt (and the other files under /llms/platforms/)
  - OpenRouter: https://openrouter.ai/docs. Runware: https://docs.runware.ai
- If a platform does not allow an action through Zernio, return "not supported on <platform>" and tell the user in chat. Never fake a capability.
- Never log or commit secrets. Keys come from environment variables. Ship `.env.example`, never `.env`.
- Dependencies must be MIT, BSD, Apache-2.0 or ISC compatible.
- Keep it small: under 3,000 lines of application code, few dependencies.
- No emojis in code, docs or commit messages. No exclamation points in marketing copy. No markdown italics in user-facing text.
- Commit after each merged work package. End commit messages with the trailer `Co-authored-by: Perplexity <noreply@perplexity.ai>`.
- Voice: funny, warm, very Gen Z, a little sexy and cheeky, never cruel. Jager teases the user and never shames anyone.
- Every supported language must be complete and idiomatic, with no untranslated or mixed-language strings.

## 3. The app

### 3.1 Architecture

```
You (WhatsApp / Telegram)
        |
     Zernio  <---- your connected social accounts
        |  webhook
   Jager server (yours)
     |- channel/   inbound and outbound chat via Zernio
     |- social/    typed Zernio wrapper: accounts, posts, comments, delete, hide, reply
     |- brain/     OpenRouter client, prompts, JSON-schema intents, model fallback, budget guard
     |- intents/   chat message to structured intent
     |- sprints/   state machine and confirmation protocol
     |- scheduler/ weekly reminder, timers, quiet hours
     |- store/     SQLite: settings, sprint state, append-only action log
     |- i18n/      EN and FR catalogues
     |- cli/       jager doctor, jager connect-check, jager export-log
        |
   OpenRouter / Runware (optional)
```

Stack (change only with a written reason in `docs/DECISIONS.md`): Python 3.12 (preferred because of the library requirement) with FastAPI, SQLite, APScheduler, pytest, Docker (non-root, `./data` volume). A mock Zernio server must let the whole app run offline in tests.

### 3.2 Platforms

Zernio's docs list 12 social platforms: **X, Instagram, Facebook, LinkedIn, TikTok, YouTube, Pinterest, Reddit, Bluesky, Threads, Google Business Profile, Snapchat.** Zernio states that comments can be read, replied to, hidden and deleted across nine platforms but does not name them, and does not say which networks allow listing or deleting posts. The Zernio integrator must build a **capability matrix** by testing and reading docs, and the site and chat must only claim what it shows.

### 3.3 Chat features

- **Recap:** "what did I post this week?" returns a numbered list (platform, snippet, date).
- **Delete:** "delete 2 and 4", "delete everything from tonight". Always confirmed.
- **Keep:** "keep 3" protects a post from future sprints.
- **Timers:** "delete everything I post tonight, an hour after I post it" creates an auto-delete rule with scope, window and expiry.
- **Comments:** groups new comments (needs a reply, question, praise, spam, troll) and serves them one at a time with actions: send draft, edit, hide, delete, skip.
- **Reply drafting** in the user's voice, from a short style note learned from their last 20 posts.
- **Weekly reminder** at a chosen day and time (default Sunday 18:00, user timezone, quiet hours respected): what you posted, how many comments wait, "start a sprint?".
- **Sprints:** comment sprint, cleanup sprint, night sprint. State machine `proposed, confirmed, running, paused, done, cancelled`, always ending with a summary.
- **Commands** in English and French: status, help, pause, resume, stop.

### 3.4 Python library

The public API must exist and be documented:

```python
from jager import Jager

jager = Jager.from_env()      # reads ZERNIO_API_KEY, OPENROUTER_API_KEY, ...
jager.weekly_recap()
jager.sprint("comments")      # also "cleanup" and "night"
```

The server, the CLI and the library share the same core. Publishing to PyPI is optional; `pip install git+https://github.com/paulfxyz/jager` must work.

### 3.5 Safety (non-negotiable, one test each)

1. No delete, hide or reply without explicit confirmation in the same chat, except auto-delete rules the user created with a clear scope and expiry.
2. Confirmation restates exactly what will happen ("Delete 2 posts (2, 4) for good? Reply YES"). Only the confirmation word in the right language, from the owner, within 10 minutes counts.
3. Only the owner can command Jager (owner ID match). Others are ignored and logged.
4. Webhook signature verified on every request.
5. `JAGER_DRY_RUN=true` by default: everything works except the final API call, which is logged.
6. Append-only action log of every proposed, confirmed, executed and failed action; `jager export-log` dumps JSON.
7. Rate limits and backoff; bulk deletes in small batches.
8. Prompt-injection defence: posts and comments are untrusted data inside delimited blocks; the model cannot act without the confirmation layer.
9. Daily spend ceiling `JAGER_DAILY_BUDGET_USD` (default 0.50).
10. Privacy: content goes only to the chosen OpenRouter model (and Runware if images are on). No telemetry.

### 3.6 Configuration

```
ZERNIO_API_KEY=
ZERNIO_WEBHOOK_SECRET=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=            # cheap default
JAGER_FALLBACK_MODELS=       # comma-separated, different provider
RUNWARE_API_KEY=             # optional
JAGER_CHANNEL=telegram       # or whatsapp
JAGER_OWNER_ID=
JAGER_TIMEZONE=Europe/Lisbon
JAGER_LANGUAGE=en
JAGER_RECAP=sunday 10:00
JAGER_DRY_RUN=true
JAGER_DAILY_BUDGET_USD=0.50
PORT=8080
```

Pick a low-cost JSON-capable default model plus a fallback from another provider. Document expected weekly cost in `docs/COSTS.md`. Respect any model the user sets.

## 4. The website (jager.social)

Static HTML, CSS and JS, no framework, generated by one Python build script (`tools/build_site.py`) that writes English at the root and French in `/fr/`. It deploys to any static host.

### 4.1 Design system: "The Night Shift"

Bold, different, neo-brutalist, nocturnal. The page is one night, from 21:00 to 09:00.

- **Colours:** midnight `#07061a`, ink `#0d0b1f`, violet `#2b1a6b`, hot pink `#ff2e7e`, acid yellow `#e4ff3a`, peach `#ffb98a`, cream `#fff4e6`.
- **Type:** Bricolage Grotesque 800 for display (tight tracking, uppercase headings), Instrument Serif italic for accent words inside headings, JetBrains Mono for labels and code. Self-host the fonts.
- **Shapes:** thick 3px ink borders, hard offset shadows (6 to 8px in pink, acid or ink), rotated stickers, pill chips, tilted phone mockup with a pink hard shadow.
- **Fixed HUD:** a small clock (21:00 to 09:00 as you scroll) with a moon that turns into a sun, plus a thin scroll progress bar under the nav.
- **Paw cursor:** a custom paw-print cursor via a CSS data URI (fallback to the default cursor on touch devices).
- **Drunk text:** body copy in the hero and story is blurred and wobbly ("drunk"); tapping or clicking it makes it sharp ("sober"). A footer toggle "Drunk mode: ON/OFF" stores the choice in a cookie. A mono hint under the hero reads "blurry? that's you at 2 AM. tap the text to focus." Respect `prefers-reduced-motion`.
- **Motion:** reveal-on-scroll, a ticker band, a rotating hero line ("Tonight's mistake: texting your ex / quote-tweeting your boss / rating a kebab shop one star / ..."), and a sticky phone in the story section.
- **Accessibility:** real contrast, focus states, `lang` attribute, reduced-motion fallback, no horizontal scroll at 375px.

### 4.2 Pages and sections (home, in order)

1. **Nav:** logo "jager." with a pink dot, links What is it, The night, Try it, Setup, FAQ; language dropdown; MIT badge; acid GitHub button. Mobile: burger menu; the language list becomes a fixed full-width sheet.
2. **Hero:** badges (Free, MIT licence, "0 servers of ours"); headline "POST DRUNK. WAKE UP *clean.*"; blurred subline (free open-source buddy in WhatsApp or Telegram); buttons "View on GitHub" and "What is this?"; a Product Hunt pill with a live countdown to Thursday 3 December 2026; tilted phone with a WhatsApp/Telegram skinned chat that plays a short scripted conversation; a rotating MIT sticker.
3. **Ticker:** Free, MIT licensed, Bring your own keys, WhatsApp, Telegram, Weekly sprints, No signup, Open source.
4. **What is Jager?** (cream): one-paragraph explainer; three problem cards (the 2 AM post, the comment pile-up, the archive anxiety); who it is for chips (Creators, Founders, Community managers, Job seekers, Night owls); a "never" list (never posts for you, never deletes without a sprint or your OK, never sees your passwords, never stores your data on our servers); comparison table Jager vs a social dashboard (where you use it, deleting, comments, who runs it, price).
5. **One night with Jager** (story): sticky phone beside four chapters timed 21:00, 23:30, 02:00, 09:00 (plug in the keys, start a night sprint, go be a menace, the morning recap). Each chapter has a replay button and a "More details" disclosure. WhatsApp/Telegram preview toggle.
6. **Try it:** an interactive chat sandbox that understands the example commands, with suggestion chips: "what did I post this week?", "start a comment sprint", "delete everything I post in the next 8 hours, 1 hour after", "delete 2 and 4". It must handle confirmation (YES), keep, comment sprints and unknown input gracefully, in both languages.
7. **Platforms** (dark): "Twelve networks. One buddy." Five pills (Recap, Delete, Hide comments, Draft replies, Timers) and 12 cards with each network's icon and a one-line joke. A small note: what Jager can do on each network depends on what that network lets Zernio do, and Jager says so in chat when something is not possible.
8. **The stack** (cream): "Three keys. That's the product." Cards for Zernio, OpenRouter, Runware (optional); flow diagram Your accounts, Zernio, Jager, OpenRouter/Runware; row of platform logos.
9. **Make it yours** (pink): "Not just a repo. A kit." Three cards: clone and run (Docker), import in Python (snippet), prompt your agents (download button for `jager-build-prompt.md`). A "Runs on" row: laptop, Raspberry Pi, small VPS, any Docker host, your own agent stack.
10. **Product Hunt launch** (dark): "Thursday the 3rd. Mark it." Big countdown (days, hours, minutes, seconds, ticking every second), a three-step timeline (Now: open source, MIT, public repo; Thu 3 Dec 2026: Product Hunt launch; After: your sprints, your translations, your pull requests), buttons GitHub and Product Hunt.
11. **MIT / take it:** outlined "MIT" word, "Take it. Change it. Ship it.", a terminal card (`git clone`, `cp .env.example .env`, `docker compose up -d`), a line that English and French are available and 28 more languages are waiting.
12. **FAQ** (cream, `details` elements): is it really free, how do I connect accounts, can I use it in my own stack, when do you launch, chat vs dashboard, what the AI sees, which languages, safety of deletes, which platforms.
13. **Closer:** "Sober up, *cyber.*" with GitHub button.
14. **Footer** (same pattern as iris.online and digital.spot): "© 2026 Enki Ltd. Released under the MIT License", company number, address, ask@jager.social, drunk-mode toggle, sister-project line (Iris, Digital Spot), disclaimer (software as is, trademarks belong to their owners, not affiliated with Jägermeister, Zernio, WhatsApp, Telegram or Meta, "Please drink and post responsibly").

**Setup page:** four steps (Zernio key, pick channel WhatsApp or Telegram, AI key, run it with `.env` and Docker), a "Before you start" checklist, a "What happens when you message Jager" flow, "Other ways to run it" (Python import and prompt download), cost note, MIT note, contribute note, closer.

**404 page:** "Lost? Classic. This page went home early."

### 4.3 Languages

- English at `/`, French at `/fr/`, `hreflang` and canonical tags, translated metadata and Open Graph tags.
- The language selector lists the **top 30 languages in the world including Hebrew and Arabic**. Only English and French are real links; the other 28 are visible but disabled and show a toast "Not translated yet. Translations are welcome on GitHub." under a "Translations welcome" separator. Adding a language must mean adding one catalogue.
- The chat sandbox, story scripts, toasts, FAQ and every string exist in both languages.

### 4.4 Files and SEO

`index.html`, `setup.html`, `fr/index.html`, `fr/setup.html`, `404.html`, `night.css`, `night.js`, `chat.js`, `fonts.css`, `favicon.svg`, `og.png` (1200x630, "free, open source, MIT, jager.social"), `robots.txt`, `sitemap.xml` (all four pages), `.htaccess` (redirect retired pages such as login, signup, pricing, platforms, channels, how, faq, terms, privacy, cookies, gdpr to the home page), `jager-build-prompt.md`, `assets/fonts`, `assets/icons` (platform icons plus GitHub, WhatsApp, Telegram). Do not publish internal specs or build scripts on the web root. Footer facts and the MIT notice replace separate legal pages.

## 5. Repository layout

```
jager/
  README.md  LICENSE  CHANGELOG.md  SECURITY.md  CONTRIBUTING.md
  .env.example  Dockerfile  docker-compose.yml  pyproject.toml
  docs/        ARCHITECTURE.md DECISIONS.md SAFETY.md SETUP.md COSTS.md VOICE.md CAPABILITIES.md
  prompts/     intents.md reply-draft.md classify-comment.md recap.md
  jager/       channel/ social/ brain/ intents/ sprints/ scheduler/ store/ i18n/ cli/
  site/        sources and build_site.py, output in site/dist
  tests/       unit/ e2e/ evals/ mocks/
  .github/     workflows/ ISSUE_TEMPLATE/
```

## 6. Agent team

| # | Agent | Owns | Deliverable |
|---|---|---|---|
| 1 | Architect | skeleton, `docs/ARCHITECTURE.md`, `DECISIONS.md`, CI | Repo that builds, lints and tests; interfaces for all modules. Runs first and alone. |
| 2 | Zernio Integrator | `social/`, `channel/`, `docs/CAPABILITIES.md` | Typed client, webhook with signature check, per-platform capability matrix, mock Zernio server. |
| 3 | Brain Engineer | `brain/`, `intents/`, `prompts/` | OpenRouter client with fallbacks and budget guard, intent schema, injection-hardened prompts, an eval set of 60+ multilingual messages. |
| 4 | Sprint Engineer | `sprints/`, `scheduler/`, `store/` | State machine, confirmation protocol, weekly reminder, auto-delete rules, migrations, action log. |
| 5 | Library Engineer | `jager/__init__.py`, packaging | `Jager.from_env()`, `weekly_recap()`, `sprint()`, docs and examples; `pip install` from git works. |
| 6 | Voice and i18n Writer | `i18n/`, `docs/VOICE.md` | EN and FR catalogues, personality guide with 20 example replies. |
| 7 | Site Designer | `site/` | The full website of section 4 in EN and FR, built from one script. |
| 8 | QA and Safety Auditor | `tests/`, `docs/SAFETY.md` | Tests for all ten safety rules, scripted end-to-end chats, red-team pass with hostile comments, Playwright checks of the site. Can block a release. |
| 9 | DevOps and Docs | Docker, CI, README, `SETUP.md` | One-command run, step-by-step Zernio, WhatsApp or Telegram, OpenRouter and Runware setup, troubleshooting, issue templates, release workflow. |
| 10 | Reviewer | read-only | Gates every merge for scope creep, secrets, licences and unsupported claims; writes `CHANGELOG.md`. |

## 7. Site QA checklist (Agent 8)

- Desktop 1366 and mobile 375 for all five pages in both languages: no horizontal scroll, no console errors, no clipped or overlapping text, no unstyled flashes.
- Countdown ticks every second and targets 2026-12-03 08:01 UTC.
- Language dropdown: English and French navigate, the other 28 only toast. Works on mobile.
- Chat sandbox in both languages: recap, "delete 2 and 4" then YES, keep, timer rule, comment sprint, gibberish.
- Story chapters play, replay and expand in both languages.
- Drunk mode toggle persists via cookie; tapping text focuses it; reduced motion respected.
- Every CTA goes to https://github.com/paulfxyz; the Product Hunt button goes to https://www.producthunt.com.
- The platform grid shows exactly the 12 Zernio platforms.
- View the rendered screenshots of every page before shipping.

## 8. Deployment (website)

- Any static host works. If your host blocks FTP from the build machine, upload a zip through the host's file manager, then **flush the host's page cache**; a stale cache serving old HTML with deleted CSS looks like a broken, unstyled page.
- Verify the live site in a real browser (bot protection can block plain HTTP clients), check that the stylesheet loads, and delete any temporary installer or gist.
- Never paste hosting or FTP passwords into a chat; use your host's secret store or SSH keys.

## 9. Definition of done

- `docker compose up -d` starts the app with only `.env` filled in; the Python import example works.
- A scripted chat against the mock Zernio passes: recap, delete with confirmation, wrong confirmation cancels, comment sprint, weekly reminder, auto-delete rule, pause and resume.
- Every safety rule has a failing-then-passing test. Dry run is the default and documented loudly.
- The capability matrix shows what Jager really does per platform; unsupported actions say so in chat.
- The website matches section 4 in both languages and passes section 7.
- README explains in plain language what Jager is, the three keys, a five-minute setup, what he never does and the weekly cost.
- MIT licence, copyright Enki Ltd. No secrets in git history; a secret scan passes.
- The repository stays private until the checklist is green, then waits for the owner to make it public.

## 10. Reporting

Each agent finishes with a message of at most 10 lines: what was built, what was tested, what is missing, and any claim it could not verify. The orchestrator ends with one summary for the owner: what works, what Zernio cannot do per platform, estimated weekly cost, open questions and the exact commands to try it.

## 11. Open items to flag to the owner

- The GitHub repo link on the site is a placeholder until the repo is public.
- The Product Hunt link is generic until a launch page exists.
- The `ask@jager.social` mailbox must exist.
- The Python import snippet on the site describes the intended API; keep the site and the library in sync.
- Which networks allow post deletion through Zernio is unverified until the capability matrix is built.

## 12. Order of work

1. Architect (alone).
2. Zernio Integrator, Brain Engineer, Sprint Engineer, Voice and i18n Writer and Site Designer in parallel against the interfaces.
3. Library Engineer once the core stabilises.
4. QA and Safety Auditor from the first testable build to the end.
5. DevOps and Docs once the app runs end to end.
6. Reviewer gates every merge.
7. Orchestrator integrates, runs all tests and `jager doctor` against the mock, deploys the site, tags `v0.1.0`.

Start now: read the Zernio docs, then run the Architect.
