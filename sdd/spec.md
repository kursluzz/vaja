# vaja — Specification

> Source of truth for requirements, architecture and feature specs.
> Progress and open questions live in [status.md](status.md).
> Architecture decisions live in [decisions/](decisions/).

---

## 0. Baseline — current state (as of 2026-09-28, commit `0094969`)

Factual description of what the code does today. Items marked *(inferred)* were
not verified by running the system.

### 0.1 Components

| Component | State |
|---|---|
| `db` — PostgreSQL 16 (alpine) | Defined in `docker-compose.yml`, data in `$DATA_DIR/postgresql`, healthcheck via `pg_isready` |
| `api` — FastAPI | Code exists in `api/`; **not** in `docker-compose.yml` yet (run locally via `make api-run`) |
| `bot` — aiogram | Empty (`bot/.gitkeep`) |
| `nginx`, `certbot`, `watchtower` | Not started (placeholders in `docker-compose.yml`) |
| CI/CD | None (no `.github/workflows/`) |
| Docs site | Empty `docs/` reserved for MkDocs |

### 0.2 Code layout and conventions

```
api/
├── main.py              # FastAPI app, /health, includes users router + module REGISTRY
├── core/                # shared: config, database, User model/schemas/router
│   ├── config.py        # pydantic-settings, reads .env (POSTGRES_*)
│   ├── database.py      # async engine (pool 5/+10), AsyncSessionLocal, Base, get_db
│   ├── models.py        # User
│   ├── schemas.py       # UserCreate, UserResponse
│   └── router.py        # /users
└── modules/             # feature modules, self-registering
    ├── __init__.py      # VajaModule dataclass, REGISTRY, register()
    └── tasks/           # enums.py, models.py, schemas.py, router.py
```

Conventions the code follows:
- Feature modules register themselves via `register(VajaModule(...))` in their
  `__init__.py`; `api/main.py` imports the module and includes every router in
  `REGISTRY`.
- `get_db` commits on success and rolls back on exception — handlers only
  `flush()`, never `commit()`.
- Async SQLAlchemy 2.0 (`Mapped[...]`, `mapped_column`), Pydantic v2 schemas.
- Ruff: py312, line length 88, rules `E,F,I,UP`, double quotes; `alembic/` excluded.

### 0.3 Data model

**users**

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` PK | |
| `telegram_user_id` | `BIGINT` | unique, indexed, not null |
| `created_at` | `TIMESTAMPTZ` | default `now()` |

**tasks**

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` PK | |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE CASCADE`, indexed |
| `title` | `VARCHAR(255)` | not null |
| `description` | `TEXT` | nullable |
| `due_date` | `TIMESTAMPTZ` | nullable |
| `priority` | `VARCHAR(10)` | not null; values `low` / `medium` / `high` (Python enum, default `medium`) |
| `category` | `VARCHAR(50)` | nullable, indexed |
| `is_done` | `BOOLEAN` | not null, default `false` |
| `created_at` | `TIMESTAMPTZ` | default `now()` |
| `updated_at` | `TIMESTAMPTZ` | default `now()`, ORM `onupdate` |

Migrations: `47ce47e9f3a3` (users) → `9be21264373d` (tasks).

### 0.4 API (implemented)

No authentication. The caller identifies the user by passing an ID.

| Method | Path | Behaviour |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |
| `POST` | `/users/` | body `{telegram_user_id}` → `201` user; `409` if it exists |
| `GET` | `/users/{telegram_user_id}` | `200` user; `404` if missing |
| `GET` | `/tasks/?user_id=` | all tasks of that user (no filter, sort or pagination) |
| `POST` | `/tasks/?user_id=` | create task → `201` |
| `GET` | `/tasks/{id}?user_id=` | `200`; `404` if missing or owned by another user |
| `PUT` | `/tasks/{id}?user_id=` | **partial** update (only fields sent) → `200`; `404` as above |
| `DELETE` | `/tasks/{id}?user_id=` | `204`; `404` as above |

`user_id` on `/tasks` is the internal `users.id`, not the Telegram ID.

### 0.5 External integrations

None implemented. `pyproject.toml` declares the `anthropic`, `groq` and
`elevenlabs` dependencies (group `ai`), and `.env.example` holds their keys.

### 0.6 Tooling

- `uv` dependency groups: `api`, `bot`, `ai`, `dev`.
- Makefile: `up`, `down`, `ps`, `api-logs`, `db-up`, `db-logs`, `db-connect`,
  `migration name=…`, `migrate`, `rollback`, `lint` (format + autofix),
  `lint-check`, `test`, `uv-sync`, `api-run`; optional `Makefile.local`.
- Tests: none exist (`api/tests/` is missing).

### 0.7 Known defects found during baseline

| ID | Defect | Verified |
|---|---|---|
| D-001 | `TaskResponse` has `mode_config` instead of `model_config`, so Pydantic raises `PydanticUserError` on import and **the API cannot start** | yes — **fixed** |
| D-002 | `alembic/env.py` imports the non-existent `api.models`, so `make migration` / `make migrate` fail (the imports were not updated after the module refactor) | yes — **fixed** |
| D-003 | `Task.priority` is a `String` column but gets a `Priority` enum object, so the insert may be rejected by asyncpg | no *(inferred)* |
| D-004 | `users.id` is `INTEGER` but `tasks.user_id` is `BIGINT` | yes (migrations) |
| D-005 | `make test` targets `api/tests/`, which does not exist | yes |
| D-006 | `make db-connect` hard-codes `taskuser` / `taskdb` instead of reading `.env` | yes |
