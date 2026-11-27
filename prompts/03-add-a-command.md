# Prompt 3: add a command or sprint, safely

---

Repo: https://github.com/paulfxyz/jager. I want a new capability: **<DESCRIBE IT>**.

Before writing code:

1. Read `docs/LEARN.md`, `docs/SAFETY.md` and `src/jager/core.py`.
2. Tell me which files you will touch and which safety rules the feature interacts with. Does it delete, hide, reply or send anything? If yes, it needs the confirmation flow (`open_pending` + `_execute`), a capability check (`capabilities.can`) before asking, dry-run support and log entries.
3. If it depends on a Zernio endpoint, find the endpoint in https://docs.zernio.com/llms.txt, cite the URL in a code comment and add the method to the `SocialAPI` protocol, `ZernioClient` **and** `MockZernio`. Do not guess endpoint shapes.

Then implement:

4. Rules in `intents.py` for English and French, a handler `_i_<kind>` in `core.py`, strings in `i18n.py` (both languages).
5. Tests: the happy path, the cancel path, the dry-run path, the unsupported-network path. Add the attack you would try if you wanted to break it.
6. Run `pytest -q` and `ruff check src tests`; update `CHANGELOG.md` and the docs.

Non-negotiable: nothing destructive happens without an explicit YES; an AI answer can never be a YES; list numbers never shift.
