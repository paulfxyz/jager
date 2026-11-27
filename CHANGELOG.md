# Changelog

Format: [Keep a Changelog](https://keepachangelog.com), versioning: [SemVer](https://semver.org).

## [0.1.0] - 2026-11-27 ("Hirsch")

First public release. Launching on Product Hunt on Thursday 3 December 2026.

### Added
- Chat commands in English and French: recap, delete, keep, timers, comment sprints, cleanup sprint, status, pause.
- Weekly reminder with quiet hours and restart-safe delivery.
- Zernio client with retries, idempotency keys, caching and pacing.
- Honest capability matrix for 12 networks, generated into the docs and tested against them.
- Optional OpenRouter brain with model fallbacks, spend cap and an injection-hardened prompt.
- Signed-webhook server with dedupe, owner check, size cap and rate limit.
- SQLite store with an append-only action log.
- `jager demo` (offline), `jager doctor`, `jager capabilities`, `jager webhook-setup`, `jager export-log`.
- Hardened Docker image and compose file.
- Website (EN and FR) in `site/`, and Markdown build prompts in `prompts/`.
- Easter eggs. We are not saying how many.
