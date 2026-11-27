# Troubleshooting

Start with `jager doctor`. It checks config, keys and Zernio, and says what to fix.

| Symptom | Likely cause | Fix |
|---|---|---|
| `jager serve` exits: "ZERNIO_WEBHOOK_SECRET is empty" | By design: an unsigned webhook is an open door | Set any long random string, `openssl rand -hex 32`, then `jager webhook-setup <url>` |
| Jager never answers | Webhook not reaching you, or you are not the owner | Is the tunnel up? Does the URL end in `/webhooks/zernio`? Is `JAGER_OWNER_ID` your number/id? Look at `docker compose logs` and `jager export-log` (`ignored-stranger` means the owner id did not match) |
| Log shows `bad-signature` | Secret differs between Zernio and `.env` | Re-run `jager webhook-setup` with the current secret |
| He says "Dry run: I pretended" | Dry run is on (the default) | `JAGER_DRY_RUN=false`, restart |
| "[no delete]" next to a post | The network does not allow it (Instagram, TikTok, Snapchat) | Delete it by hand, see [CAPABILITIES](CAPABILITIES.md) |
| Delete fails for a post that was not published with Zernio | Unpublish takes the Zernio post id; outside posts may not be deletable that way | Jager reports the failure instead of guessing. Delete by hand |
| TikTok comments fail with a platform limitation | The account is connected through a developer app | Connect it through the TikTok for Business app |
| Weekly reminder did not arrive | Quiet hours, or no chat route learned yet | Message Jager once (he remembers where to find you), check `JAGER_QUIET_HOURS` and `JAGER_TIMEZONE` |
| Replies arrive twice | Zernio redelivered an event | Jager dedupes by event id. If you see this, open an issue with the log |
| `429` or WhatsApp error 131056 | Too many messages to one recipient | Jager retries with backoff. WhatsApp tolerates about 10 messages a minute per recipient |
| AI features stopped | Daily budget reached, or no key | Say `status`. Raise `JAGER_DAILY_BUDGET_USD` or wait for tomorrow. Rules still work |
| "something went wrong on my side" | An unexpected error, already logged | `jager export-log`, look for `error` entries, open an issue (no secrets are in the log) |

Still stuck? Open an issue with the output of `jager doctor` and `jager --version`.
