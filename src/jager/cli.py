"""The command line: `jager doctor`, `jager demo`, `jager serve` and friends.

Run ``jager --help``. The commands are designed to teach: `jager demo` lets you
play with Jager offline in 10 seconds, and `jager doctor` tells you in plain
words what to fix when something does not work.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from . import capabilities as cap
from .config import ConfigError, Settings

STAG = r"""
        \|/ \|/
         \\|//
          \|/
          /^\    jager {v}
         ( o o)  "Ya-guerr." Pronounced like that. Please.
         (  v  ) 56 herbs, 0 regrets (until Monday).
        __|   |__
"""


def _demo(lang: str) -> int:
    from .core import Jager
    j = Jager.demo(lang)
    print(STAG.format(v=__version__))
    print("Offline demo: a fake Zernio, no keys, nothing real is touched. Type 'help'. Ctrl-D to leave.\n")
    print("jager>", j.t("hello"))
    try:
        while True:
            line = input("you> ").strip()
            if line:
                for part in j.handle(line):
                    print("jager>", part)
    except (EOFError, KeyboardInterrupt):
        print("\njager> Cheers. Drink some water.")
    return 0


def _doctor() -> int:
    """Check everything, say what is wrong in human words, exit non-zero if anything is."""
    problems = 0

    def line(ok: bool, text: str, fix: str = "") -> None:
        nonlocal problems
        print(("  ok   " if ok else "  FAIL ") + text + ("" if ok or not fix else f"\n         fix: {fix}"))
        problems += 0 if ok else 1

    print(f"Jager doctor {__version__}\n")
    try:
        s = Settings.from_env()
    except ConfigError as exc:
        line(False, f"configuration: {exc}", "check your .env against .env.example")
        return 1
    line(True, "configuration parses")
    line(bool(s.zernio_api_key), "ZERNIO_API_KEY present", "https://zernio.com/dashboard/api-keys")
    line(bool(s.zernio_webhook_secret), "ZERNIO_WEBHOOK_SECRET present", "any long random string, e.g. `openssl rand -hex 32`")
    line(bool(s.owner_id), "JAGER_OWNER_ID present (only this person can command Jager)", "your phone number or Telegram id")
    line(bool(s.openrouter_api_key), "OPENROUTER_API_KEY present (optional: without it Jager uses rules only)")
    print(f"  info dry run is {'ON (safe: nothing gets deleted)' if s.dry_run else 'OFF (live: deletes are real)'}")
    if s.zernio_api_key:
        from .zernio import ZernioClient, ZernioError
        try:
            n = ZernioClient(s.zernio_api_key, s.base_url).ping()
            line(n > 0, f"Zernio reachable, {n} account(s) connected", "connect accounts in the Zernio dashboard")
        except ZernioError as exc:
            line(False, f"Zernio call failed: {exc}", "check the API key and your connection")
    print("\nAll good. Go forth and post responsibly." if not problems else f"\n{problems} thing(s) to fix.")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="jager", description="Post drunk. Wake up clean.")
    p.add_argument("--version", action="version", version=f"jager {__version__}")
    sub = p.add_subparsers(dest="cmd")
    d = sub.add_parser("demo", help="talk to Jager offline (fake Zernio, no keys)")
    d.add_argument("--lang", default="en", choices=["en", "fr"])
    sub.add_parser("doctor", help="check your setup and say what to fix")
    sub.add_parser("serve", help="run the webhook server")
    sub.add_parser("capabilities", help="print what each network lets Jager do")
    sub.add_parser("recap", help="print the weekly recap")
    sub.add_parser("export-log", help="dump the append-only action log as JSON")
    w = sub.add_parser("webhook-setup", help="register this server's URL with Zernio")
    w.add_argument("url", help="public URL, e.g. https://jager.example.com/webhooks/zernio")
    sub.add_parser("shots", help="(you know what this does)")
    a = p.parse_args(argv)

    if a.cmd == "demo":
        return _demo(a.lang)
    if a.cmd == "doctor":
        return _doctor()
    if a.cmd == "capabilities":
        yes = lambda b: "yes" if b else " - "   # noqa: E731
        print(f"{'network':<16}{'del post':>9}{'read':>6}{'reply':>7}{'hide':>6}{'del cmt':>9}")
        for r in cap.table():
            print(f"{r['name']:<16}{yes(r['delete_post']):>9}{yes(r['read_comments']):>6}{yes(r['reply_comment']):>7}"
                  f"{yes(r['hide_comment']):>6}{yes(r['delete_comment']):>9}")
        return 0
    if a.cmd == "shots":
        print("Ein, zwei, g'suffa. (Now drink water. This is a social media tool, not a bar.)")
        return 0
    if a.cmd in {"serve", "recap", "export-log", "webhook-setup"}:
        try:
            from .core import Jager
            s = Settings.from_env()
            if a.cmd == "serve":
                import uvicorn

                from .server import create_app
                uvicorn.run(create_app(s), host=s.host, port=s.port, log_level="info")
                return 0
            j = Jager.from_env()
            if a.cmd == "recap":
                print(j.recap_text())
            elif a.cmd == "export-log":
                print(json.dumps(j.store.export_log(), indent=2))
            else:
                from .zernio import ZernioClient
                r = ZernioClient(s.zernio_api_key, s.base_url).create_webhook(a.url, s.zernio_webhook_secret)
                print("webhook registered:", json.dumps(r.get("webhook", r), indent=2))
            return 0
        except ConfigError as exc:
            print(f"Config problem: {exc}", file=sys.stderr)
            return 2
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
