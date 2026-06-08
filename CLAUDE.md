# CLAUDE.md — vaja project instructions

> Instructions for Claude Code. Read this before doing anything in this repository.
> For system architecture and design decisions, see ARCHITECTURE.md.

---

## Project

**vaja** — self-hosted Telegram bot for task management with voice input and AI intelligence.
Stack: Python 3.12, FastAPI, PostgreSQL 16, aiogram 3, Docker Compose, nginx, Let's Encrypt,
Groq Whisper (STT), ElevenLabs (TTS), Anthropic Claude Haiku.

---

## Core Rules

- **All code and comments in English** — no exceptions
- **Async Python everywhere** — use `async`/`await`, never blocking calls
- **`bot` never touches the database directly** — it calls `api` via HTTP only
- **Always read `ARCHITECTURE.md`** before implementing a feature or making structural changes

---

## Git Workflow

### Commits — Conventional Commits
```
feat: add voice message handler
fix: correct task due_date parsing
chore: update dependencies
docs: add API endpoint examples
refactor: extract claude service to separate module
test: add tasks CRUD integration tests
```

### Branches
```
feat/5-telegram-bot-setup
fix/12-voice-handler-crash
chore/3-watchtower-config
```
Format: `type/issue-number-short-description`

### Flow
1. Create branch from `main`
2. Implement feature
3. Open PR → merge to `main`
4. One feature per branch, one logical change per commit

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
├── docker-compose.dev.yml
├── pyproject.toml
├── .env.example
├── ARCHITECTURE.md
└── CLAUDE.md               # this file
```

---

## Makefile Commands

```bash
make up           # docker compose up -d
make down         # docker compose down
make logs         # follow api logs
make migrate      # alembic upgrade head
make migration    # alembic revision --autogenerate -m "name"
make rollback     # alembic downgrade -1
make test         # pytest
make lint         # ruff check .
```

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

## Implementing Issues — Step-by-Step Protocol

When asked to implement an issue:

1. **Present the plan** — outline approach and list all files to be created/changed
2. **Implement step by step** — each step is one discrete action:
   - create a branch
   - add a single file
   - commit and push
3. **Wait for confirmation** before moving to the next step
4. **Each step should be reviewable** — user can ask questions or propose changes

---

## What to Update When Things Change

| What changed | What to update |
|---|---|
| New service or major component | `ARCHITECTURE.md` (Services table + diagram) |
| New API endpoint | `ARCHITECTURE.md` (API Endpoints section) |
| New file or folder in repo | `ARCHITECTURE.md` (Repository Structure) |
| New `make` command | `Makefile` + this file (Makefile Commands section) |
| New env variable | `.env.example` |
| Progress on a milestone | `ARCHITECTURE.md` (Progress checklist) |

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
