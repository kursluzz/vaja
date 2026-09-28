# Contributing to vaja

Thanks for your interest in vaja! This guide covers local development setup and
how changes get from an idea to `main`.

---

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) with Docker Compose v2
- [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs Python 3.12+ for you if needed
- `make`, `git`

## Local setup

```bash
git clone https://github.com/kursluzz/vaja.git
cd vaja
make setup
make api-run
```

Open http://localhost:8000/docs to try the API in Swagger UI.

`make setup` is safe to re-run. It never overwrites existing local files. It:

1. installs all dependency groups into `.venv` (`uv sync --all-groups`)
2. creates `.env` from `.env.example` if it's missing
3. creates `docker-compose.override.yml` from `docker-compose.override.example.yml`
   if it's missing. The override exposes PostgreSQL on `localhost:5432`
4. starts the `db` container and waits until it is healthy
5. applies database migrations

### Local files

These files are gitignored and belong to your machine only:

| File | Purpose |
|---|---|
| `.env` | Secrets and settings. For local dev keep `POSTGRES_HOST=localhost` and `DATA_DIR=./vaja_data` |
| `docker-compose.override.yml` | Local Compose tweaks, e.g. publishing the DB port |
| `Makefile.local` | Optional personal `make` targets, included automatically |

API keys (`ANTHROPIC_API_KEY`, `GROQ_API_KEY`, ...) are only needed for the
features that use them. The tasks CRUD API runs without any keys.

### Troubleshooting

- **Port 5432 already in use.** Another PostgreSQL is running. Change the host port in
  `docker-compose.override.yml` (e.g. `"5433:5432"`) and set `POSTGRES_PORT=5433` in `.env`.
- **Port 8000 already in use.** Another API instance (or a debugger session) is running.
  Stop it, or run `uv run uvicorn api.main:app --reload --port 8001`.
- **`password authentication failed`.** The DB was initialized with other
  credentials. PostgreSQL applies `POSTGRES_*` only when the data directory is first
  created. Restore the old values in `.env`, or reset the DB by deleting
  `$DATA_DIR/postgresql`. **This deletes all local data.**

## Debugging in an IDE

Run uvicorn as a module. Running `api/main.py` directly only imports the app and
does not start a server.

| Setting | Value |
|---|---|
| Module | `uvicorn` |
| Parameters | `api.main:app --reload` |
| Working directory | project root |
| Interpreter | `.venv/bin/python` |

## Everyday commands

```bash
make db-up        # start PostgreSQL
make api-run      # run the API with auto-reload
make migrate      # apply migrations
make migration name="add x to tasks"  # autogenerate a migration after model changes
make rollback     # revert the last migration
make db-connect   # psql shell inside the db container
make lint         # format + autofix with ruff
make lint-check   # check only (what CI runs)
make test         # run tests
```

Every model change needs a migration. After adding a new module with models, import
its `models` in `alembic/env.py` so autogenerate can see it.

## How work is organized

| Where | What |
|---|---|
| [GitHub Issues](https://github.com/kursluzz/vaja/issues) | Bugs, feature requests, one issue per feature |
| [GitHub Milestones](https://github.com/kursluzz/vaja/milestones) | Release progress (v0.x) |
| [`sdd/`](sdd/) | Specs: requirements, feature specs, architecture decisions (ADRs), task breakdown |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System design overview |
| [`ROADMAP.md`](ROADMAP.md) | Vision and future ideas |

Larger features are specified in `sdd/spec.md` before implementation. If your change
contradicts the spec, raise it in the issue first.

## Making a change

1. Find or open an issue, and comment that you're working on it.
2. Create a branch from `main` named `type/issue-number-short-description`:
   ```
   feat/5-telegram-bot-setup
   fix/12-voice-handler-crash
   docs/26-contributing-guide
   ```
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/),
   one logical change per commit:
   ```
   feat: add voice message handler
   fix: correct task due_date parsing
   docs: add API endpoint examples
   ```
4. Run `make lint-check` and `make test`.
5. Open a PR to `main` with `Closes #<issue>` in the description.

## Code style

- Python 3.12+, async everywhere (`async`/`await`, no blocking calls)
- Ruff: line length 88, double quotes, sorted imports (`make lint` fixes most issues)
- All code, comments, docs, commits and PRs in English
- `bot` never touches the database. It calls `api` over HTTP
- Every task query filters by `user_id`. Users never see each other's data
