# Install Jager

Time needed: about 15 minutes, 10 of which are clicking through dashboards.
You will end up with a Jager that answers you in Telegram or WhatsApp.

> Rule zero: Jager ships in **dry-run mode**. He will pretend to delete things and tell you so.
> Watch him behave for a day before you flip the switch. Trust is earned, even by herbal liqueurs.

## What you need

| Thing | Why | Where |
|---|---|---|
| A [Zernio](https://zernio.com) account | Connects your social accounts and your chat app | Free to start, see [COSTS](COSTS.md) |
| A machine that stays on | Runs Jager: laptop, Raspberry Pi, small VPS | Anything with Docker or Python 3.11+ |
| A way for Zernio to reach it | Webhooks need a public HTTPS URL | Cloudflare Tunnel, Caddy, nginx, ngrok |
| An [OpenRouter](https://openrouter.ai) key (optional) | The AI brain. Rules work without it | https://openrouter.ai/keys |

## Step 1. Zernio: accounts and chat channel

1. Create an API key: <https://zernio.com/dashboard/api-keys>. A key looks like `sk_` plus 64 hex characters. Zernio shows it once, copy it now.
2. Connect the social accounts Jager should look after (see [CAPABILITIES](CAPABILITIES.md) for what he can do on each). Zernio's guide: <https://docs.zernio.com/guides/connecting-accounts.mdx>.
3. Connect **one chat channel** for talking to Jager:
   - **Telegram:** create a bot with [@BotFather](https://t.me/BotFather), connect it in Zernio, press Start in the bot. Zernio's Telegram guide: <https://docs.zernio.com/llms/platforms/telegram.txt>.
   - **WhatsApp:** Zernio offers a shared sandbox number for testing, no purchase and no Meta review needed: <https://docs.zernio.com/platforms/whatsapp/sandbox.mdx>. For daily use you will want your own number.

## Step 2. Configure

```bash
git clone https://github.com/paulfxyz/jager && cd jager
cp .env.example .env
```

Fill in `.env` (every variable is explained in [CONFIGURATION](CONFIGURATION.md)). The five that matter:

```bash
ZERNIO_API_KEY=sk_...
ZERNIO_WEBHOOK_SECRET=$(openssl rand -hex 32)   # paste the generated value, not the command
JAGER_OWNER_ID=+351912345678                      # your number, Telegram id or username
OPENROUTER_API_KEY=sk-or-...                      # optional
JAGER_TIMEZONE=Europe/Lisbon
```

`JAGER_OWNER_ID` is your identity. Only messages from this person are obeyed, everybody else is ignored. Leave it empty and nobody gets in.

## Step 3. Start Jager

### Option A: Docker (recommended)

```bash
docker compose up -d
docker compose logs -f           # Ctrl-C to stop watching, Jager keeps running
```

The container is non-root, read-only and listens on `127.0.0.1:8080` only. That is deliberate: you put a tunnel or reverse proxy in front (next step) instead of exposing a raw port to the internet.

### Option B: Python

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
jager serve                      # reads .env from your environment, see below
```

`jager serve` reads environment variables, not the `.env` file by itself. Load it first: `set -a; source .env; set +a`.

To keep it running after you log out, use a systemd unit:

```ini
# /etc/systemd/system/jager.service
[Unit]
Description=Jager
After=network-online.target

[Service]
User=jager
WorkingDirectory=/opt/jager
EnvironmentFile=/opt/jager/.env
ExecStart=/opt/jager/.venv/bin/jager serve
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/jager/data

[Install]
WantedBy=multi-user.target
```

### Option C: as a library

```bash
pip install git+https://github.com/paulfxyz/jager
```

```python
from jager import Jager
jager = Jager.from_env()
print(jager.weekly_recap())
```

No server needed if you only use it from your own code. You lose the chat webhook, naturally.

## Step 4. Give Zernio a way in

Zernio must reach `POST /webhooks/zernio` over HTTPS. The quickest way is a Cloudflare quick tunnel:

```bash
cloudflared tunnel --url http://localhost:8080
# prints something like https://random-words.trycloudflare.com
```

For something permanent use a named tunnel, or Caddy/nginx on a domain you own. Then register the URL with Zernio (this reuses your webhook secret):

```bash
jager webhook-setup https://random-words.trycloudflare.com/webhooks/zernio
```

(In Docker: `docker compose exec jager jager webhook-setup <url>`.)

## Step 5. Check, then talk

```bash
jager doctor
```

`doctor` checks your config, your keys and whether Zernio answers, and tells you in plain words what to fix. Then open your chat and write **`help`** to Jager. He answers, introduces himself and you are live.

## Step 6. From dry run to the real thing

1. Ask `what did I post this week?`, then `delete 1`, then `yes`. Jager says "Dry run: I pretended to delete...". Nothing was touched.
2. Check what he would have done: `jager export-log`.
3. Happy? In `.env` set `JAGER_DRY_RUN=false` and restart (`docker compose up -d`).
4. Delete something small and embarrassing first. A good test post is one you will not miss.

## Uninstall

```bash
docker compose down -v           # removes the container and ./data is untouched unless you delete it
rm -rf data                      # the diary (action log) goes too
```

Disconnect your accounts in the Zernio dashboard and delete the webhook there. Jager keeps nothing of yours anywhere else, because there is nowhere else.

Trouble? **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**.
