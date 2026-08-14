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

When starting the web server, always `source .envrc` first (sets `SIZE`, `PLAYERS`, `SHARED`):

```bash
source .envrc && make run
```

After changing `pyproject.toml` constraints, run `poetry lock` (or `poetry update`) yourself. `make install` uses `poetry lock --no-update` locally and will not bump versions.

## Validation

For small changes (copy, spacing, docs, isolated helpers with unit coverage), skip e2e:

```bash
make check && make test-unit
```

For gameplay, routes, templates that affect flows, or anything that could break the pomace path, run the full suite (server must already be up locally):

```bash
make all HEADLESS=true
```

Agents always pass `HEADLESS=true`. Humans can omit it to watch the browser.

## Tests

- Unit tests: `tests/test_*.py` — no server required.
- E2e: `tests/e2e.py` via pomace/Firefox against `http://localhost:5000` (`WAIT = 0`).
  - Locally, start the app first (`source .envrc && make run` in another terminal), then `make all` (headed) or `make all HEADLESS=true`.
  - In CI, `honcho` starts web + e2e from `tests/Procfile` (headless).

## Layout

- `app/models.py` — `Board` / `Game` (persisted under `data/games/`)
- `app/autoplay.py` — non-human player AI (random move planning)
- Turn resolve is three steps: **Show Results** (tactical + combat), **Show Reinforcements**, then **Start Next Round** (applies reinforcements)
- After **Start Next Round**, players return to `State.READY` so the **Plan Moves…** button shows (ellipsis marks that planning is a follow-on step)
- `app/actions.py` — simultaneous-move resolution (`Attack`, `MassAttack`, etc.)
- `app/views.py` — Flask routes
- `app/types.py`, `app/enums.py`, `app/constants.py` — shared types and config
- `sites/` — pomace page models for e2e

## UI chrome (board view)

Player bar (HUD), grid, and status message are the main in-game stack (`.gc-play-column` in `board.html` / styles in `base.html`):

- All three must **fit vertically** in the viewport (no page scroll for that stack). Size the square grid from the remaining space (`min(100%, calc(100dvh - …))` on `.gc-play-column`); keep cells square via the `td:after { margin-top: 100% }` trick in `board.html`.
- Debug move lists sit **below the status bar** in normal flow and must not shrink or rescale the grid. It is fine if debug content extends past the bottom of the screen. Do not use a viewport-tall spacer stage that leaves a gap above debug.
- Top-align the stack (do **not** vertically center game pages).
- From `sm` and up, all three share the **same width**.
- On small screens the grid goes **full-bleed**; keep **horizontal padding** (`mx-3`) on the player bar and status so they are not edge-to-edge.

## Conventions

- Prefer `field(default_factory=...)` for mutable dataclass defaults (required on Python 3.13+).
- Keep `werkzeug` on 2.x (`<3`) so `flask-api` / pomace keep working.
- mypy uses the datafiles plugin (`plugins = "datafiles.plugins:mypy"` in `pyproject.toml`).
