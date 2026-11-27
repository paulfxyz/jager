# Contributing

Welcome. Jager is small on purpose, so a contribution can be small too.

## The easiest first pull requests

1. **Translate Jager.** Open [`src/jager/i18n.py`](src/jager/i18n.py), copy the `"fr"` entries into a new language code, translate, add the code to `LANGS` and to the validation in `config.py`. The tests fail until every key exists, and tell you which one you forgot.
2. **Add a joke.** Strings that are tuples are random variants. Add one. Keep it kind: Jager teases the user, never the people in the comments.
3. **Fix the docs.** If you got stuck during install, the docs are wrong, not you.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make test lint
```

The whole suite runs offline in under a second. If you add behaviour, add a test. If you change what a network can do, change `capabilities.py` and run `python tools/gen_capabilities.py`.

## Ground rules

- Safety rules in [docs/SAFETY.md](docs/SAFETY.md) are not negotiable. A change that weakens one will not be merged, however clever.
- Comment the **why**, not the what. This codebase is also a tutorial.
- Keep dependencies at the minimum. Every dependency is a future bug and a future audit.
- No emojis in code or commit messages. Jokes are welcome.
- Be nice. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
