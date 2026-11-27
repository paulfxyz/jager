"""Configuration.

Everything comes from environment variables (12-factor style) so the same code
runs on a laptop, a Raspberry Pi or a Docker host without edits. Secrets are
never written to disk by Jager and never logged: see ``Settings.redacted``.

Design notes
------------
* ``Settings`` is a frozen dataclass: once loaded it cannot change under your
  feet, which makes behaviour easier to reason about and to test.
* Dry run is ON by default. A new user should see what Jager *would* do before
  anything is deleted. They switch it off deliberately.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field, replace
from zoneinfo import ZoneInfo


class ConfigError(RuntimeError):
    """Raised when configuration is missing or invalid. Messages are meant for humans."""


def _bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _float(value: str | None, default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError as exc:
        raise ConfigError(f"Expected a number, got {value!r}") from exc


@dataclass(frozen=True)
class Settings:
    # --- the three keys -----------------------------------------------------
    zernio_api_key: str = ""
    openrouter_api_key: str = ""          # optional: without it Jager uses rules only
    runware_api_key: str = ""             # optional: reserved for image jobs
    zernio_webhook_secret: str = ""       # used to verify incoming webhooks

    # --- who and where ------------------------------------------------------
    owner_id: str = ""                    # phone number, Telegram id or username
    channel: str = "telegram"             # telegram | whatsapp (informational)
    timezone: str = "UTC"
    language: str = "en"                  # en | fr
    quiet_hours: str = "23:00-08:00"      # no proactive messages in this window

    # --- brain --------------------------------------------------------------
    model: str = "openai/gpt-4o-mini"
    fallback_models: tuple[str, ...] = ("google/gemini-2.0-flash-001",)
    daily_budget_usd: float = 0.50

    # --- behaviour ----------------------------------------------------------
    dry_run: bool = True                  # SAFE BY DEFAULT
    recap: str = "sunday 10:00"           # weekly reminder, local time
    confirm_ttl_s: int = 600              # a confirmation is valid for 10 minutes
    rule_poll_s: int = 300                # how often auto-delete rules look for new posts
    write_pace_s: float = 0.4             # pause between destructive API calls
    batch_size: int = 5                   # destructive calls per batch
    batch_pause_s: float = 2.0            # extra pause between batches

    # --- plumbing -----------------------------------------------------------
    base_url: str = "https://zernio.com/api/v1"
    db_path: str = "data/jager.db"
    port: int = 8080
    host: str = "127.0.0.1"               # loopback by default: put a reverse proxy or tunnel in front
    extra: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ build
    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        e = dict(os.environ if env is None else env)
        fallbacks = tuple(m.strip() for m in e.get("JAGER_FALLBACK_MODELS", "google/gemini-2.0-flash-001").split(",") if m.strip())
        s = cls(
            zernio_api_key=e.get("ZERNIO_API_KEY", ""),
            openrouter_api_key=e.get("OPENROUTER_API_KEY", ""),
            runware_api_key=e.get("RUNWARE_API_KEY", ""),
            zernio_webhook_secret=e.get("ZERNIO_WEBHOOK_SECRET", ""),
            owner_id=e.get("JAGER_OWNER_ID", ""),
            channel=e.get("JAGER_CHANNEL", "telegram").lower(),
            timezone=e.get("JAGER_TIMEZONE", "UTC"),
            language=e.get("JAGER_LANGUAGE", "en").lower()[:2],
            quiet_hours=e.get("JAGER_QUIET_HOURS", "23:00-08:00"),
            model=e.get("OPENROUTER_MODEL", e.get("JAGER_MODEL", "openai/gpt-4o-mini")),
            fallback_models=fallbacks,
            daily_budget_usd=_float(e.get("JAGER_DAILY_BUDGET_USD"), 0.50),
            dry_run=_bool(e.get("JAGER_DRY_RUN"), True),
            recap=e.get("JAGER_RECAP", "sunday 10:00"),
            base_url=e.get("ZERNIO_BASE_URL", "https://zernio.com/api/v1").rstrip("/"),
            db_path=e.get("JAGER_DB", "data/jager.db"),
            port=int(e.get("PORT", "8080")),
            host=e.get("JAGER_HOST", "127.0.0.1"),
        )
        s.validate()
        return s

    def with_(self, **changes) -> Settings:
        """Return a modified copy (Settings is frozen)."""
        return replace(self, **changes)

    # --------------------------------------------------------------- validate
    def validate(self) -> None:
        if self.language not in {"en", "fr"}:
            raise ConfigError(f"JAGER_LANGUAGE must be 'en' or 'fr', got {self.language!r}")
        try:
            ZoneInfo(self.timezone)
        except Exception as exc:  # unknown zone name
            raise ConfigError(f"JAGER_TIMEZONE {self.timezone!r} is not a valid IANA zone, e.g. Europe/Lisbon") from exc
        parse_recap(self.recap)          # raises ConfigError on bad input
        parse_quiet(self.quiet_hours)

    def require_zernio(self) -> None:
        if not self.zernio_api_key:
            raise ConfigError("ZERNIO_API_KEY is missing. Create one at https://zernio.com/dashboard/api-keys and put it in .env")

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    def redacted(self) -> dict:
        """Safe-to-print view of the config (keys are masked)."""
        def mask(v: str) -> str:
            return "" if not v else v[:3] + "..." + v[-2:] if len(v) > 8 else "***"
        d = {k: v for k, v in self.__dict__.items() if k != "extra"}
        for k in ("zernio_api_key", "openrouter_api_key", "runware_api_key", "zernio_webhook_secret"):
            d[k] = mask(d[k])
        return d


_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_recap(text: str) -> tuple[int, int, int]:
    """'sunday 10:00' -> (weekday 0=Mon, hour, minute)."""
    m = re.fullmatch(r"\s*([a-z]+)\s+(\d{1,2}):(\d{2})\s*", text.lower())
    if not m or m.group(1) not in _DAYS:
        raise ConfigError(f"JAGER_RECAP must look like 'sunday 10:00', got {text!r}")
    h, mi = int(m.group(2)), int(m.group(3))
    if not (0 <= h < 24 and 0 <= mi < 60):
        raise ConfigError(f"JAGER_RECAP has an impossible time: {text!r}")
    return _DAYS.index(m.group(1)), h, mi


def parse_quiet(text: str) -> tuple[int, int] | None:
    """'23:00-08:00' -> (minute_of_day_start, minute_of_day_end). Empty string disables."""
    if not text.strip():
        return None
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*", text)
    if not m:
        raise ConfigError(f"JAGER_QUIET_HOURS must look like '23:00-08:00', got {text!r}")
    a = int(m.group(1)) * 60 + int(m.group(2))
    b = int(m.group(3)) * 60 + int(m.group(4))
    return a, b


def in_quiet_hours(minute_of_day: int, window: tuple[int, int] | None) -> bool:
    """True if ``minute_of_day`` falls inside the quiet window (which may wrap midnight)."""
    if window is None:
        return False
    a, b = window
    return a <= minute_of_day < b if a <= b else (minute_of_day >= a or minute_of_day < b)
