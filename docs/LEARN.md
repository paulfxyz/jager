# Learn by reading Jager

Jager is small on purpose (a few thousand lines) and every file is commented like a tutorial. Read the files in the order below and you will pick up a surprising amount of real-world backend engineering: webhooks, HMAC signatures, retries, idempotency, caching, state machines, SQLite, and defending an AI feature against hostile text. Bring a drink. A glass of water, we said.

Each stop has a **Try this** you can run in under a minute. Install first: `pip install -e ".[dev]"`.

---

## Stop 1. `capabilities.py`: tell the truth

**Idea:** an API that wraps many services cannot do what a service refuses. So write the limits down as *data*, and check them before acting.

Open it and find the `MATRIX`. It is a plain dict: for each network, five booleans and a note. Everything else (the chat, the docs, the website cards) reads from it.

**Try this:** `jager capabilities` prints the table. Then run `pytest tests/test_capabilities.py -q`: one test fails if the generated docs ever disagree with the code. Documentation that cannot rot.

## Stop 2. `intents.py`: regex before AI

**Idea:** the cheapest, fastest, safest "language model" is a regular expression. Use AI only where rules give up.

Read `parse()`. Note `_norm()` (accents stripped, so "supprimé" matches) and how numbers like `2 and 4` or `1-3` are extracted. Then read `from_ai()` at the bottom: **the model proposes, the validator disposes**. It can never produce a `yes`.

**Try this:**
```python
from jager.intents import parse
print(parse("supprime 2 et 4"))        # Intent(kind='delete', numbers=[2, 4], ...)
print(parse("jager bomb"))             # an easter egg
```

## Stop 3. `zernio.py`: a polite, resilient HTTP client

**Idea:** networks fail. A good client expects it.

- `_request()` retries 429 and 5xx with exponential backoff and **jitter** (so a hundred clients do not all retry at the same millisecond), and honours `Retry-After`.
- Writes carry an **`Idempotency-Key`**, reused on retry: if a timeout hides a successful send, the retry cannot send the reply twice.
- `_get()` has a tiny TTL cache that every write clears.
- `_dt()` and `_first()` parse messy JSON without crashing: **be strict in what you send, liberal in what you accept**.

**Try this:** read `tests/test_zernio.py`. It plays Zernio with `httpx.MockTransport`: no network needed to test retries.

## Stop 4. `store.py`: SQLite as a memory (and a conscience)

**Idea:** you do not need Postgres to remember a few rows.

- WAL mode, parameterised SQL everywhere, and one transaction helper (`_tx`) so a crash cannot leave half-written state.
- `first_time(event_id)` uses `INSERT OR IGNORE` and checks `rowcount`: two simultaneous deliveries cannot both win.
- The `log` table has **triggers that abort UPDATE and DELETE**. The database itself enforces "append-only".

**Try this:** `sqlite3 data/jager.db "DELETE FROM log"` after running the demo against a real file. Watch SQLite say no.

## Stop 5. `brain.py`: an AI on a leash

**Idea:** text from strangers is not instructions.

Read the `SYSTEM_TRIAGE` prompt and `_clean()`, which strips our own `<untrusted>` tags from a comment so it cannot "close the cage" early. Then `_validate()`: only known ids, known categories, no links, max length. Then `_account()`: a daily spend cap. The model never touches the world directly.

**Try this:** `tests/test_scheduler_brain_i18n.py::test_prompt_injection_stays_in_the_cage_and_cannot_close_the_tag`.

## Stop 6. `core.py`: the heart

**Idea:** a conversation is a state machine, and state belongs in the database, not in variables.

Read `_handle()` top to bottom: pending confirmation first (YES executes, anything else cancels), then parse, then dispatch to `_i_<kind>` methods. Notice that the sprint lives in SQLite (`store.get("sprint")`), so you can restart the server mid-sprint and lose nothing.

Notice `_run_deletes()`: dry run, pacing between calls and a longer pause between batches. And that deleted entries are **flagged, not removed**, so "delete 3" can never hit a different post than the one you saw.

**Try this:** `jager demo`, then: `recap`, `delete 2`, `yes`, `delete 2` again.

## Stop 7. `scheduler.py`: the night watchman

**Idea:** make time a parameter. `tick(now)` is a plain function, so tests pass in a fake clock and never `sleep`.

Notice the weekly reminder is remembered by ISO week in the database. A restart cannot double-send it, and a late restart still sends it (catch-up), unless it is quiet hours.

## Stop 8. `server.py`: the one door to the internet

**Idea:** build the door like a nightclub's.

Read `verify_signature()`. `hmac.compare_digest` takes the same time whether the first byte or the last differs, so an attacker cannot guess a signature one character at a time. Then follow a request: size cap, signature, JSON, dedupe, **acknowledge fast and work in the background** (Zernio wants a 2xx within 5 seconds), owner check, rate limit.

**Try this:** `python examples/03_sign_a_test_webhook.py` against `jager serve`. Change one character of the body and get a 401.

## Stop 9. `i18n.py`: every word in one place

Strings live in one dict, per language. Tuples are random variants. A test checks every key exists in every language and that placeholders match between languages. Translating Jager into Spanish is a single, well-fenced task.

---

## Glossary

| Term | In one sentence |
|---|---|
| **Webhook** | The service calls *you* when something happens, instead of you asking repeatedly. |
| **HMAC** | A signature made from a secret and the message: proves who sent it and that it was not altered. |
| **Constant-time compare** | Comparing secrets in a way that does not leak how many characters matched. |
| **Idempotency key** | A label that makes "do this once" safe to retry. |
| **Backoff + jitter** | Wait longer after each failure, with randomness, so retries do not stampede. |
| **Dedupe** | Ignore the second delivery of the same event. |
| **Fail closed** | When unsure, deny. |
| **Prompt injection** | Text that tries to give instructions to an AI that was only supposed to read it. |
| **Append-only log** | A diary that cannot be edited. Cheating is harder, and so is forgetting. |
| **WAL** | SQLite's write-ahead log: crash-safe and lets readers and a writer coexist. |

## Exercises (from easy to evil)

1. Add a new easter egg phrase to `intents.py` and a reply to `i18n.py`. Add a test.
2. Add Spanish. Let the tests tell you what is missing.
3. Add a `delete older than 30 days` command. Which file changes? Which safety rule does it touch?
4. Make the recap show comment counts. Where does the data come from?
5. Try to break the confirmation: find a message that executes a delete without a YES. If you find one, that is a security report we will gladly credit.
