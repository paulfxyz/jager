"""Jager: post drunk, wake up clean.

A small, open-source (MIT) buddy that lives in your WhatsApp or Telegram,
tells you what you posted, deals with public comments and runs cleanup sprints.

Three lines to use it as a library::

    from jager import Jager

    jager = Jager.from_env()      # reads ZERNIO_API_KEY, OPENROUTER_API_KEY, ...
    print(jager.weekly_recap())   # what did I post this week?

No keys yet? Try the offline demo, which talks to a fake Zernio::

    jager = Jager.demo()
    print(jager.handle("what did I post this week?"))

Reading order for the curious (each file is heavily commented):
    capabilities.py  what each network lets us do (the honest matrix)
    zernio.py        the Zernio API client (retries, cache, pacing)
    intents.py       turn "delete 2 and 4" into a structured intent
    brain.py         the optional AI layer (OpenRouter) with a spend cap
    store.py         SQLite: state, dedupe, append-only action log
    core.py          the Jager class: conversation, sprints, confirmations
    scheduler.py     weekly reminder and auto-delete rules
    server.py        webhook receiver (signature check, dedupe, owner check)
"""

from .config import ConfigError, Settings
from .core import Jager

__version__ = "0.1.0"
__all__ = ["Jager", "Settings", "ConfigError", "__version__"]
