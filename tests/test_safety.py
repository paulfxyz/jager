"""The ten commandments. If one of these fails, do not ship."""
import time


def ask(j, *msgs):
    out = []
    for m in msgs:
        out = j.handle(m)
    return "\n".join(out)


def test_no_delete_without_yes(jager):
    ask(jager, "recap")
    before = len(jager.api._posts)
    ask(jager, "delete 1")
    assert len(jager.api._posts) == before                       # asked, did not act


def test_yes_executes_exactly_what_was_shown(jager):
    ask(jager, "recap", "delete 1")
    out = ask(jager, "yes")
    assert "deleted" in out.lower() and jager.api.calls == [("delete_post", "p1")]


def test_anything_else_cancels(jager):
    ask(jager, "recap", "delete 1")
    out = ask(jager, "hmm maybe")
    assert "Cancelled" in out and jager.api.calls == []
    assert "nothing waiting" in ask(jager, "yes").lower()         # the late YES finds nothing to confirm


def test_confirmation_expires(jager):
    ask(jager, "recap", "delete 1")
    jager.store._db.execute("UPDATE pending SET expires=?", (time.time() - 1,))
    assert "nothing waiting" in ask(jager, "yes").lower() and jager.api.calls == []


def test_dry_run_never_calls_the_api(dry):
    ask(dry, "recap", "delete 1")
    out = ask(dry, "yes")
    assert "Dry run" in out and dry.api.calls == []


def test_unsupported_network_is_refused_before_asking(jager):
    ask(jager, "recap")
    out = ask(jager, "delete 3")                                 # #3 is the Instagram dog
    assert "Instagram" in out and jager.store.current_pending() is None


def test_keep_protects(jager):
    ask(jager, "recap", "keep 1")
    assert "protected" in ask(jager, "delete 1").lower() and jager.store.current_pending() is None


def test_numbers_never_shift_after_deleting(jager):
    ask(jager, "recap", "delete 2", "yes")
    assert "already gone" in ask(jager, "delete 2")


def test_action_log_is_append_only(jager):
    ask(jager, "recap")
    import sqlite3

    import pytest
    with pytest.raises(sqlite3.DatabaseError):
        jager.store._db.execute("DELETE FROM log")
    with pytest.raises(sqlite3.DatabaseError):
        jager.store._db.execute("UPDATE log SET status='lol'")


def test_every_destructive_step_is_logged(jager):
    ask(jager, "recap", "delete 1", "yes")
    kinds = [(r["kind"], r["status"]) for r in jager.store.export_log()]
    assert ("propose", "open") in kinds and ("confirm", "yes") in kinds and ("delete_post", "ok") in kinds


def test_comment_delete_needs_yes_and_sprint_flow(jager):
    ask(jager, "start a comment sprint")
    out = ask(jager, "delete")
    assert "for good" in out and not any(c[0] == "delete_comment" for c in jager.api.calls)
    ask(jager, "yes")
    assert any(c[0] == "delete_comment" for c in jager.api.calls)


def test_pause_blocks_everything(jager):
    ask(jager, "pause")
    assert "paused" in ask(jager, "delete all").lower()


def test_errors_never_crash_or_leak(jager):
    jager.api.posts = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("secret sk-123"))
    out = ask(jager, "recap")
    assert "sk-123" not in out and "went wrong" in out


def test_timer_rule_needs_confirmation_then_deletes(jager):
    out = ask(jager, "delete everything I post tonight, 1 hour after")
    assert "YES" in out and jager.store.active_rules() == []
    ask(jager, "yes")
    assert len(jager.store.active_rules()) == 1
    assert "Stopped 1" in ask(jager, "stop rules")
