"""Tiny data classes: the shapes Jager passes around.

Zernio's JSON is rich, and its field names vary a little between platforms.
We squash it into these small, boring objects ONCE, at the edge (see
``zernio.py``), so the rest of the code never has to care. Boring is a
feature: boring code does not wake you up at 3 AM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Account:
    id: str
    platform: str            # Zernio slug, e.g. "twitter", "instagram"
    handle: str = ""         # @name, for display


@dataclass(frozen=True)
class Post:
    id: str                  # id we use to act on it (Zernio post id when we have one)
    account_id: str
    platform: str
    text: str
    created: datetime        # timezone-aware, UTC
    url: str = ""

    @property
    def key(self) -> str:
        """Stable identity across restarts: used by the protect list and dedupe tables."""
        return f"{self.platform}:{self.account_id}:{self.id}"


@dataclass
class Comment:
    id: str
    post_id: str
    account_id: str
    platform: str
    text: str
    author: str = ""
    created: datetime | None = None
    is_own: bool = False         # the account's own reply: never moderate yourself
    is_hidden: bool = False
    # Filled in by the brain (or by plain rules when there is no AI key):
    category: str = "other"      # reply | question | praise | spam | troll | other
    draft: str = ""

    @property
    def key(self) -> str:
        return f"{self.platform}:{self.account_id}:{self.post_id}:{self.id}"


@dataclass
class Intent:
    """What the user wants, in a machine-friendly shape.

    ``kind`` is one of the constants in ``intents.py``. ``numbers`` are 1-based
    list positions ("delete 2 and 4"). ``args`` carries extras such as a
    timer window or a reply text.
    """
    kind: str
    numbers: list[int] = field(default_factory=list)
    args: dict = field(default_factory=dict)
    source: str = "rules"        # rules | ai
