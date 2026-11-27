"""Example 1: talk to Jager with no keys, no network, no risk.

Run it:  python examples/01_offline_demo.py

Jager.demo() wires him to a fake Zernio (src/jager/mock.py) that obeys the same
rules as the real one. Try the same messages you would type in WhatsApp.
"""
from jager import Jager

jager = Jager.demo()

for message in [
    "what did I post this week?",   # numbered recap of the last 7 days
    "delete 1 and 3",               # 3 is an Instagram post: Jager explains he cannot delete it
    "yes",                          # the explicit confirmation. Anything else would cancel.
    "jager bomb",                   # an easter egg. There are more. Find them.
]:
    print(f"you   > {message}")
    for reply in jager.handle(message):
        print(f"jager > {reply}\n")
