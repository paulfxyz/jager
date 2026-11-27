# Update Jager

Updating should be boring. Here is the boring version.

## Before you update (30 seconds)

1. Read the [CHANGELOG](../CHANGELOG.md) for versions between yours and the new one. Look for **Breaking** and **Config** lines.
2. Back up the diary and state (one file):

   ```bash
   sqlite3 data/jager.db ".backup 'data/jager.backup.db'"     # safe even while Jager is running
   # no sqlite3? stop Jager first and copy the file:  docker compose stop && cp data/jager.db data/jager.backup.db
   ```

3. Know your version: `jager --version` (or `docker compose exec jager jager --version`).

## Docker

```bash
git pull
docker compose up -d --build
docker compose exec jager jager doctor
```

## Python

```bash
git pull                            # if you cloned
pip install -U .                    # or: pip install -U git+https://github.com/paulfxyz/jager
sudo systemctl restart jager        # if you use the systemd unit from INSTALL.md
jager doctor
```

## Library users

```bash
pip install -U git+https://github.com/paulfxyz/jager
```

Pin a version in production: `pip install git+https://github.com/paulfxyz/jager@v0.1.0`.

## After you update

- Run `jager doctor`. It spots new required settings.
- Compare `.env` with the new `.env.example`: `diff .env .env.example`. New variables always have safe defaults, but it is nice to know.
- Say `status` to Jager in chat. He answers if he is alive.
- Consider a day in dry-run (`JAGER_DRY_RUN=true`) after a big jump, especially across a minor version (0.1 to 0.2).

## Versioning

Jager follows [semantic versioning](https://semver.org). While we are on `0.x`, minor versions may change behaviour, and we will say so in the changelog. Patch versions only fix things.

## Database changes

The schema is created idempotently (`CREATE TABLE IF NOT EXISTS`). When a release needs a migration it runs automatically at startup, is listed in the changelog, and is covered by the backup you just made.

## Roll back

```bash
docker compose down
git checkout v0.1.0                 # the version you were on
cp data/jager.backup.db data/jager.db
docker compose up -d --build
```

The action log is append-only by design (the database refuses edits), so restoring a backup also restores the honest history up to that point.

## When Zernio changes something

Networks change what apps may do. If a capability changes, we update [`capabilities.py`](../src/jager/capabilities.py), regenerate [CAPABILITIES.md](CAPABILITIES.md) and release a patch. You can also watch [Zernio's changelog](https://docs.zernio.com/llms/changelog.txt).
