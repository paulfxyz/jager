# What does it cost?

Jager is free (MIT). You pay your providers directly for what you use. Check each provider's current pricing before you start, because prices change and this page may not.

## Zernio

From Zernio's pricing pages when this was written ([social](https://docs.zernio.com/pricing/social.mdx), [inbox](https://docs.zernio.com/pricing/inbox.mdx)):

- Social accounts bill per connected account, with the first 2 free. **X bills every API call**, passed through at cost, and needs a card on file.
- Outbound chat messages (Jager's replies to you) bill per message, with 10,000 free each month. A chatty Jager sends a few dozen a week.
- Zernio's docs also say that from 1 December 2026 pay-per-use items come from a prepaid balance. Read [their pricing](https://docs.zernio.com/pricing.mdx) for the current rules.

## OpenRouter (optional)

Jager makes a call only when the rules do not understand a message, and one batched call per comment sprint. With a small model, our estimate is a fraction of a cent per call: cents per month for normal use. This is an estimate, not a promise. Jager tracks the cost OpenRouter reports and **stops asking the AI at `JAGER_DAILY_BUDGET_USD`** (default $0.50 a day).

Want it cheaper? Remove the key. Jager keeps working from rules.

## Where the server runs

A Raspberry Pi, an old laptop or the smallest VPS is plenty. Jager idles at almost nothing: one thread waking every 20 seconds, SQLite, three dependencies.

## How Jager saves you money (the efficiency tricks)

- Rules first, AI only when stumped.
- All comments in a sprint go to the model in **one** request.
- 30-second cache on reads; writes clear it.
- Newest-first pagination that stops at the edge of the time window (matters on X, where every page is billed).
- Rules poll the networks only while a rule is active and something can be due.
