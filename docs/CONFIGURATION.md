# Configuration

Everything is an environment variable (with Docker: the `.env` file). Defaults are safe. Config is validated at startup and `jager doctor` explains problems in plain words.

| Variable | Default | What it does |
|---|---|---|
| `ZERNIO_API_KEY` | | **Required.** Your Zernio key. |
| `ZERNIO_WEBHOOK_SECRET` | | **Required for `jager serve`.** Signs and verifies webhooks. Server refuses to start without it. |
| `JAGER_OWNER_ID` | | Who may command Jager: phone, Telegram id or username. Empty means nobody (fail closed). |
| `OPENROUTER_API_KEY` | | Optional AI brain. Without it Jager uses rules only. |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Primary model (cheap, JSON-capable). |
| `JAGER_FALLBACK_MODELS` | `google/gemini-2.0-flash-001` | Comma-separated. Tried in order if the primary is down. Use a different provider. |
| `JAGER_DAILY_BUDGET_USD` | `0.50` | When reached, the AI goes quiet and rules carry on. |
| `RUNWARE_API_KEY` | | Reserved for image jobs. |
| `JAGER_CHANNEL` | `telegram` | `telegram` or `whatsapp` (informational). |
| `JAGER_TIMEZONE` | `UTC` | IANA name, e.g. `Europe/Lisbon`. Drives the weekly reminder and quiet hours. |
| `JAGER_LANGUAGE` | `en` | `en` or `fr`. |
| `JAGER_RECAP` | `sunday 10:00` | Weekly reminder: day and time, local. |
| `JAGER_QUIET_HOURS` | `23:00-08:00` | No proactive messages in this window (may wrap midnight). Empty disables. |
| `JAGER_DRY_RUN` | `true` | While true nothing is deleted, hidden or sent. |
| `JAGER_HOST` | `127.0.0.1` | Bind address. The Docker image sets `0.0.0.0` inside the container; compose publishes loopback only. |
| `PORT` | `8080` | Listen port. |
| `JAGER_DB` | `data/jager.db` | SQLite file. |
| `ZERNIO_BASE_URL` | `https://zernio.com/api/v1` | Override for testing. |

Advanced knobs (pacing, batch sizes, confirmation lifetime) live in `Settings` in [`config.py`](../src/jager/config.py) and are deliberately not environment variables: the defaults are chosen to be polite to the networks, and you should have to read the code to change them.
