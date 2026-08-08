# Agent Notes

See [README.md](README.md) for the player-facing game description.

Implementation: Flask app with YAML game state via [datafiles](https://github.com/jacebrowning/datafiles).

## Commands

| Command | Purpose |
|---------|---------|
| `make` / `make install` | Install Poetry deps into `.venv` |
| `make all` | Format, typecheck, unit tests, and e2e (CI status) |
| `make check` | Format (`autoflake` / `isort` / `black`) then `mypy` |
| `make test` | Unit + e2e |
| `make test-unit` | `pytest` only |
| `make run` | Dev server with livereload on http://127.0.0.1:5000 |
| `make serve` | Gunicorn (production-style) |

After changing `pyproject.toml` constraints, run `poetry lock` (or `poetry update`) yourself. `make install` uses `poetry lock --no-update` locally and will not bump versions.

## Validation

After any code change, run the full suite (server must already be up locally):

```bash
make all HEADLESS=true
```

Agents always pass `HEADLESS=true`. Humans can omit it to watch the browser.

## Tests

- Unit tests: `tests/test_*.py` — no server required.
- E2e: `tests/e2e.py` via pomace/Firefox against `http://localhost:5000` (`WAIT = 0`).
  - Locally, start the app first (`make run` in another terminal), then `make all` (headed) or `make all HEADLESS=true`.
  - In CI, `honcho` starts web + e2e from `tests/Procfile` (headless).

## Layout

- `app/models.py` — `Board` / `Game` (persisted under `data/games/`)
- `app/autoplay.py` — non-human player AI (random move planning)
- Turn resolve is four steps: **Apply Results** (tactical + combat), **Show Reinforcements**, **Apply Reinforcements**, then **Start Next Round**
- `app/actions.py` — simultaneous-move resolution (`Attack`, `MassAttack`, etc.)
- `app/views.py` — Flask routes
- `app/types.py`, `app/enums.py`, `app/constants.py` — shared types and config
- `sites/` — pomace page models for e2e

## Conventions

- Prefer `field(default_factory=...)` for mutable dataclass defaults (required on Python 3.13+).
- Keep `werkzeug` on 2.x (`<3`) so `flask-api` / pomace keep working.
- mypy uses the datafiles plugin (`plugins = "datafiles.plugins:mypy"` in `pyproject.toml`).
