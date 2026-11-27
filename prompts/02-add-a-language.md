# Prompt 2: add a language to Jager

---

Repo: https://github.com/paulfxyz/jager. Add **<LANGUAGE>** (code: `<xx>`) to Jager.

1. Read `docs/VOICE.md` and `src/jager/i18n.py`. Match the voice: warm, cheeky, a bit Gen Z, never cruel; translate as an adaptation, not word for word, and keep jokes landing in the new language. Keep `{placeholders}` identical. Where a value is a tuple (variants), provide the same number of variants or more.
2. Add the language code to `LANGS` in `i18n.py` and to the allowed languages in `Settings.validate()` in `config.py`.
3. Add that language's command words to `src/jager/intents.py` (yes/no words, delete, keep, recap, sprint, hide, skip, help, status, pause, resume). `_norm()` strips accents, so write patterns without them.
4. Add tests in `tests/` mirroring `test_french_conversation_works` and a parametrised case in `test_intents.py` for your language.
5. Run `pytest -q` and `ruff check src tests`. Everything must pass. The suite fails if any key is missing.
6. If the language is right-to-left, say so in your summary instead of guessing about layout.

Report: files changed, any phrase you were unsure about (so a native speaker can review), and the test output.
