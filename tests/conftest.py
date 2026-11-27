"""Shared fixtures. Every test gets a fresh in-memory diary and a fake Zernio, so tests are fast and isolated."""
import pytest

from jager import Jager


@pytest.fixture
def jager():
    """A demo Jager with dry run OFF (so deletes really hit the mock) and zero pacing."""
    return Jager.demo()


@pytest.fixture
def dry():
    j = Jager.demo()
    j.s = j.s.with_(dry_run=True)
    return j
