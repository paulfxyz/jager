"""Parsing: English, French, accents, typos in spirit, and a hostile AI."""
import pytest

from jager.intents import from_ai, numbers_in, parse


@pytest.mark.parametrize("text,kind", [
    ("what did I post this week?", "recap"),
    ("qu'est-ce que j'ai publié cette semaine ?", "recap"),
    ("delete 2 and 4", "delete"), ("supprime 2 et 4", "delete"),
    ("delete all", "delete_all"), ("supprime tout", "delete_all"),
    ("keep 3", "keep"), ("garde 1", "keep"),
    ("start a comment sprint", "sprint_comments"), ("lance un sprint commentaires", "sprint_comments"),
    ("cleanup sprint", "sprint_cleanup"),
    ("YES", "yes"), ("oui", "yes"), ("no", "no"), ("annule", "no"),
    ("help", "help"), ("aide", "help"), ("status", "status"),
    ("jager bomb", "jagerbomb"), ("56 herbs", "jagerbomb"),
    ("stop", "stop"), ("skip", "skip"), ("hide", "hide"),
    ("blorp", "unknown"),
])
def test_kinds(text, kind):
    assert parse(text).kind == kind


def test_numbers():
    assert numbers_in("2 and 4") == [2, 4]
    assert numbers_in("1-3") == [1, 2, 3]
    assert numbers_in("2, 4 et 4") == [2, 4]
    assert numbers_in("999 and 0") == []          # out of range ignored


def test_timer_parses_window_and_delay():
    i = parse("delete everything I post in the next 8 hours, 1 hour after I post it")
    assert i.kind == "timer" and i.args == {"hours": 8, "delay_min": 60}
    assert parse("supprime tout ce que je publie ce soir").kind == "timer"


def test_long_input_is_truncated():
    assert parse("delete " + "9 " * 5000).kind in {"delete", "unknown"}   # must not hang or explode


def test_ai_can_never_say_yes():
    # The model proposes, the validator disposes: a confirmation must come from a human.
    assert from_ai({"kind": "yes"}).kind == "unknown"
    assert from_ai({"kind": "rm -rf"}).kind == "unknown"
    assert from_ai({"kind": "delete", "numbers": [2, "x", 9999, -1]}).numbers == [2]
