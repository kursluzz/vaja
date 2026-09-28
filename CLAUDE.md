# CLAUDE.md — vaja project instructions

> Instructions for Claude Code. Read this before doing anything in this repository.
> For system architecture and design decisions, see ARCHITECTURE.md.

---

## Project

**vaja** — self-hosted Telegram bot for task management with voice input and AI intelligence.
Stack: Python 3.12, FastAPI, PostgreSQL 16, aiogram 3, Docker Compose, nginx, Let's Encrypt,
Groq Whisper (STT), ElevenLabs (TTS), Anthropic Claude Haiku.

---

\

- **All code and comments in English** — no exceptions
- **Async Python everywhere** — use `async`/`await`, never blocking calls
- **`bot` never touches the database directly** — it calls `api` via HTTP only
- **Always read `sdd/status.md`** first, then `sdd/spec.md` and `ARCHITECTURE.md` before implementing a feature or making structural changes

---

## Git Workflow

Branch naming, Conventional Commits and the PR flow are defined in
`CONTRIBUTING.md` ("Making a change"). Follow it exactly:
- Branch: `type/issue-number-short-description`, created from `main`
- One feature per branch, one logical change per commit
- PR description contains `Closes #N`

---

## Code Style

- **Formatter/linter:** ruff (`make lint`)
- **Line length:** 88
- **Quotes:** double (`"`)
- **Imports:** isort-compatible (ruff handles this)
- **Python target:** 3.12+

### Patterns to follow
```python
# Dependencies via FastAPI DI
async def get_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskResponse]:
    ...

# SQLAlchemy — async sessions only
result = await db.execute(select(Task).where(Task.user_id == user_id))

# Pydantic models for all request/response validation
class TaskCreate(BaseModel):
    title: str
    due_date: datetime | None = None
    priority: int = 0
```

---

## Project Structure

```
vaja/
├── api/                    # FastAPI service
│   ├── main.py             # app init, router registration
│   ├── config.py           # pydantic-settings config
│   ├── database.py         # engine, session, Base
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas (request/response)
│   ├── routers/
│   │   ├── tasks.py        # /tasks CRUD
│   │   └── ai.py           # /ai/* endpoints
│   └── services/
│       └── claude.py       # Anthropic integration
├── bot/                    # aiogram Telegram bot
│   ├── main.py
│   ├── handlers/
│   │   ├── tasks.py        # text message handlers
│   │   ├── voice.py        # voice message handlers
│   │   └── callbacks.py    # inline keyboard handlers
│   └── services/
│       ├── groq.py         # Whisper STT
│       └── elevenlabs.py   # ElevenLabs TTS
├── alembic/                # DB migrations
├── nginx/
│   └── nginx.conf
├── docs/                   # MkDocs (deployed to vaja.dev/docs)
├── Makefile
├── docker-compose.yml
├── docker-compose.override.example.yml
├── pyproject.toml
├── .env.example
├── ARCHITECTURE.md
└── CLAUDE.md               # this file
```

---

## Makefile Commands

```bash
make setup        # first-time local setup: deps, .env, override, db, migrations
make db-up        # start PostgreSQL
make api-run      # run the API locally with --reload
make up / down    # docker compose up -d / down
make ps           # docker compose ps
make api-logs     # follow api logs
make db-logs      # db logs
make db-connect   # psql inside the db container
make migrate      # alembic upgrade head
make migration name="..."  # alembic revision --autogenerate
make rollback     # alembic downgrade -1
make lint         # ruff format + ruff check --fix
make lint-check   # ruff format --check + ruff check (CI)
make test         # pytest
make uv-sync      # uv sync --all-groups
```

Full developer guide: `CONTRIBUTING.md`.

---

## API Endpoints

### Tasks CRUD
```
GET    /tasks          — list tasks (filtered by user)
POST   /tasks          — create task
GET    /tasks/{id}     — get single task
PUT    /tasks/{id}     — update task
DELETE /tasks/{id}     — delete task
```

### AI
```
POST /ai/parse         — parse natural language → structured task
POST /ai/prioritize    — prioritize task list
POST /ai/summarize     — daily digest
POST /ai/suggest       — suggest subtasks for a task
```

### System
```
GET  /health           — health check
```

---

## Database

- **PostgreSQL 16**, async via `asyncpg`
- **Migrations:** Alembic — always generate a migration for every model change
- **`users` table** — `id`, `telegram_user_id`, `created_at`
- **`tasks` table** — `id`, `user_id` (FK), `title`, `description`, `due_date`, `priority`, `is_done`, `created_at`, `updated_at`
- All task queries **must filter by `user_id`** — users never see each other's data
- Users are auto-registered on first message (no explicit sign-up)

---

## AI Integration

- **Model:** `claude-haiku-*` (cheapest, fast enough for parsing)
- **Structured output:** prompt Claude to return JSON, parse with Pydantic
- **Never use Claude Sonnet/Opus** for routine tasks — cost control matters
- Claude integration lives in `api/services/claude.py` only — no direct Anthropic calls from `bot`

---

## Docker & Deployment

- **CI/CD:** push to `main` → GitHub Actions (lint + test + build) → GHCR → Watchtower auto-deploys
- **Deploy = `git push`** — no manual SSH, no manual container restarts
- **Secrets** — never commit `.env`, use `.env.example` as template
- **Volumes** — all persistent data in `$DATA_DIR` (configured in `.env`)

---

## Specs & Issue Tracking

The workflow follows the `/sdd` skill (Specification-Driven Development).

| Lives in | What |
|---|---|
| `sdd/` | Requirements, feature specs, ADRs, detailed task list (`TASK-*` in `sdd/status.md`) |
| GitHub Issues | Bugs, external feature requests, one issue per feature/milestone (not per TASK) |
| GitHub Milestones | v0.x release progress |
| `ROADMAP.md` | Vision and future ideas only, no progress tracking |
| `docs/` | Public MkDocs site only, no internal specs |

Rules:
- **Link, don't copy:** an issue links to its spec section (`sdd/spec.md#...`), the spec links back to the issue (`Tracking: #N`)
- **Progress is automatic:** PRs use `Closes #N`; never update GitHub manually to report progress
- **`TASK-*` stays local:** never mirrored to GitHub
- **Bugs go to GitHub Issues;** if a bug reveals a spec gap, the fix PR updates the spec too
- **Spec conflicts with code:** stop and ask, do not silently pick one

---

## What to Update When Things Change

| What changed | What to update |
|---|---|
| New service or major component | `ARCHITECTURE.md` (Services table + diagram) |
| New API endpoint | `ARCHITECTURE.md` (API Endpoints section) |
| New file or folder in repo | `ARCHITECTURE.md` (Repository Structure) |
| New `make` command | `Makefile` + this file (Makefile Commands section) |
| New env variable | `.env.example` |
| Progress on a task | `sdd/status.md` (Tasks) |
| Requirement, spec or decision change | `sdd/spec.md`, `sdd/decisions/ADR-*.md` |

---

## Milestones

| Version | Scope |
|---|---|
| v0.1 | Database & Basic CRUD API |
| v0.2 | AI Integration |
| v0.3 | CI/CD & Deployment |
| v0.4 | SSL & Certbot |
| v0.5 | Telegram Bot |
| v0.6 | Speech to Text (Groq Whisper) |
| v0.7 | Text to Speech (ElevenLabs) |
