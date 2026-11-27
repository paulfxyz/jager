"""Example 2: use Jager as a library inside your own app, bot or cron job.

Needs ZERNIO_API_KEY in the environment (and optionally OPENROUTER_API_KEY).
Safe to run: JAGER_DRY_RUN defaults to true, so nothing gets deleted.

    export ZERNIO_API_KEY=sk_...
    python examples/02_library_usage.py
"""
from jager import Jager

jager = Jager.from_env()

# 1) The same recap Jager sends you on Sundays. It returns text, you decide what to do with it.
print(jager.weekly_recap())

# 2) Start a comment sprint. It returns the first messages; feed the owner's answers to handle().
for line in jager.sprint("comments"):
    print(line)

# 3) Everything the owner could type in chat also works from code:
for line in jager.handle("keep 1"):
    print(line)
