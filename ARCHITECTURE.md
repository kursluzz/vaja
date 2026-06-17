# vaja — Architecture

> This document describes the project architecture and key decisions. Used as context for AI development sessions.

---

## Project Overview

**vaja** (Voice AI Assistant) — a self-hosted Telegram bot for task management with voice input and AI intelligence.

- **Language:** Python 3.12+
- **Repository:** github.com/YOUR_USERNAME/vaja
- **License:** MIT
- **Deployment:** self-hosted home server, static IP, Docker Compose

---

## Services (Docker Compose)

```
┌─────────────────────────────────────────┐
│           Docker Compose                │
│                                         │
│  ┌─────────┐     ┌─────────┐           │
│  │  nginx  │────▶│   api   │           │
│  │  :443   │     │ FastAPI │           │
│  └─────────┘     └─────────┘           │
│       ▲               │                │
│       │           ┌───▼─────┐          │
│  Telegram          │   bot   │          │
│  webhook           │ aiogram │          │
│                   └───┬─────┘          │
│                       │                │
│                   ┌───▼─────┐          │
│                   │   db    │          │
│                   │Postgres │          │
│                   └─────────┘          │
│                                         │
│  ┌──────────┐   ┌──────────┐          │
│  │watchtower│   │ certbot  │          │
│  └──────────┘   └──────────┘          │
│                                         │
│  ┌──────────┐  ← optional              │
│  │  ollama  │    local LLM server      │
│  └──────────┘                          │
└─────────────────────────────────────────┘
```

| Service | Image | Purpose |
|---------|-------|---------|
| `api` | python:3.12 | FastAPI REST API |
| `bot` | python:3.12 | aiogram Telegram bot |
| `db` | postgres:16 | Database |
| `nginx` | nginx:alpine | Reverse proxy + SSL termination |
| `certbot` | certbot/certbot | Let's Encrypt SSL auto-renewal |
| `watchtower` | containrrr/watchtower | Auto-deploy new Docker images |
| `ollama` | ollama/ollama | Local LLM server (optional, replaces Anthropic) |

---

## Technology Stack

### Backend API (`api`)
- **FastAPI 0.115** — REST API framework
- **SQLAlchemy 2.0** — async ORM
- **asyncpg** — async PostgreSQL driver
- **Alembic** — database migrations
- **Pydantic 2.9** — data validation

### Telegram Bot (`bot`)
- **aiogram 3.x** — async Telegram Bot framework
- Webhook mode (not long polling) — Telegram pushes updates to our domain
- `bot` calls `api` via internal Docker network over HTTP

### AI Layer
- LLM and STT are pluggable via the Provider Layer (see below)
- **ElevenLabs** — text-to-speech, bot replies with voice messages
- Structured outputs from LLM via JSON mode

### Text-to-Speech (TTS)
- Bot always replies with text first
- Inline keyboard button `🔊 Listen` under each response
- On button press — ElevenLabs generates audio → bot sends voice message
- ElevenLabs chosen for natural voice quality, has free tier (10k chars/mo)

### Database
- **PostgreSQL 16** — primary database
- Data stored in Docker volume (persists across container restarts)
- **Multi-user** — every user gets their own isolated data
- `users` table stores Telegram `user_id`, created automatically on first message
- All tasks filtered by `user_id` — users never see each other's data

### Networking & SSL
- **Domain** with A-record pointing to server's static IP
- **nginx** — accepts HTTPS :443, proxies to `api` and `bot`
- **Let's Encrypt** via certbot — free SSL, auto-renewal every 90 days
- Router ports open: 80 (certbot challenge), 443 (HTTPS)

---

## Feature Modules

vaja is built as a collection of feature modules. Each module is self-contained and registers itself into the application — adding a new module requires no changes to core code.

### Module Structure

```
api/modules/<name>/
├── __init__.py     # declares and registers the module
├── models.py       # SQLAlchemy models (if needed)
├── schemas.py      # Pydantic schemas
├── router.py       # FastAPI router (/module-name/*)
└── service.py      # business logic, calls providers

bot/modules/<name>/
├── __init__.py
└── handlers.py     # aiogram message/callback handlers
```

### Module Registry

```python
# api/modules/__init__.py

class VajaModule:
    name: str           # "tasks"
    display_name: str   # "Task Management"
    router: APIRouter

REGISTRY: list[VajaModule] = []

def register(module: VajaModule):
    REGISTRY.append(module)
```

```python
# api/main.py — routers registered automatically

from api.modules import REGISTRY

for module in REGISTRY:
    app.include_router(module.router)
```

### Current Modules

| Module | Prefix | Description |
|--------|--------|-------------|
| `tasks` | `/tasks` | Task management CRUD + AI parsing |
| `news` | `/news` | News aggregation by user interests |

---

## Provider Layer

LLM and STT providers are pluggable. Switching providers requires only a `.env` change — feature modules are unaffected.

### Abstraction

```python
# api/core/providers/base.py

class LLMProvider(ABC):
    async def complete(self, prompt: str, system: str) -> str: ...
    async def complete_json(self, prompt: str, system: str) -> dict: ...

class STTProvider(ABC):
    async def transcribe(self, audio: bytes, language: str = "auto") -> str: ...
```

### Provider Directory

```
api/core/providers/
├── __init__.py          # get_llm() / get_stt() factory functions
├── base.py              # LLMProvider, STTProvider abstract classes
├── llm/
│   ├── anthropic.py     # Anthropic Claude (default)
│   └── ollama.py        # Ollama local models
└── stt/
    ├── groq.py          # Groq Whisper API (default)
    └── whisper.py       # faster-whisper local
```

### Configuration

```env
# .env — switch providers without touching code
LLM_PROVIDER=anthropic        # "anthropic" | "ollama"
ANTHROPIC_API_KEY=sk-...
ANTHROPIC_MODEL=claude-haiku-4-5

OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:14b

STT_PROVIDER=groq             # "groq" | "whisper"
GROQ_API_KEY=gsk_...
WHISPER_MODEL=large-v3        # small | medium | large-v3
```

### Available Providers

| Type | Provider | Notes |
|------|----------|-------|
| LLM | `anthropic` | Default. Claude Haiku, ~$1/mo |
| LLM | `ollama` | Local. Model set via `OLLAMA_MODEL` |
| STT | `groq` | Default. Groq Whisper API, free tier |
| STT | `whisper` | Local. faster-whisper on CPU via `WHISPER_MODEL` |

---

## CI/CD

```
git push main
     ↓
GitHub Actions
  - lint (ruff)
  - tests (pytest)
  - build Docker image
  - push to GHCR (GitHub Container Registry)
     ↓
Watchtower on server
  - checks GHCR every 5 minutes
  - if new image → pull + restart container
```

Deploy = `git push`. No SSH into server, no manual commands.

---

## Repository Structure

```
vaja/
├── api/                    # FastAPI service
│   ├── main.py             # app init, registers all module routers
│   ├── core/               # shared infrastructure
│   │   ├── config.py       # pydantic-settings (all env vars)
│   │   ├── database.py     # engine, session, Base
│   │   ├── dependencies.py # FastAPI DI (get_db, get_llm, get_stt)
│   │   └── providers/      # pluggable AI providers
│   │       ├── __init__.py # get_llm() / get_stt() factories
│   │       ├── base.py     # LLMProvider, STTProvider ABC
│   │       ├── llm/
│   │       │   ├── anthropic.py
│   │       │   └── ollama.py
│   │       └── stt/
│   │           ├── groq.py
│   │           └── whisper.py
│   └── modules/            # feature modules
│       ├── __init__.py     # ModuleRegistry + register()
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── router.py   # /tasks/*
│       │   └── service.py
│       └── news/
│           ├── __init__.py
│           ├── models.py
│           ├── schemas.py
│           ├── router.py   # /news/*
│           └── service.py
├── bot/                    # aiogram Telegram bot
│   ├── main.py             # registers all module handlers
│   ├── core/
│   │   └── base_handler.py
│   └── modules/            # bot-side feature modules
│       ├── tasks/
│       │   └── handlers.py
│       └── news/
│           └── handlers.py
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
└── CLAUDE.md
```

---

## API Endpoints

### Tasks Module
```
GET    /tasks          — list tasks
POST   /tasks          — create task
GET    /tasks/{id}     — get single task
PUT    /tasks/{id}     — update task
DELETE /tasks/{id}     — delete task
POST   /tasks/parse    — parse natural language → task
POST   /tasks/suggest  — suggest subtasks
```

### News Module
```
GET    /news           — get news feed for user
POST   /news/setup     — configure interests
POST   /news/sources   — manage RSS sources
```

### System
```
GET  /health           — health check
```

---

## External Services & Costs

| Service | Usage | Cost |
|---------|-------|------|
| Telegram Bot API | Webhook, messages | Free |
| Anthropic Claude Haiku | LLM (default provider) | ~$0.50-1/mo |
| Groq Whisper | STT (default provider) | Free (28k sec/mo) |
| ElevenLabs | Text-to-speech (TTS) | Free (10k chars/mo) |
| Ollama | LLM (local alternative) | $0 |
| faster-whisper | STT (local alternative) | $0 |
| Let's Encrypt | SSL certificate | Free |
| GHCR | Docker images | Free |
| GitHub Actions | CI/CD | Free (open source) |

**Total with cloud providers: ~$1/month. Fully local: $0/month.**

---

## Architecture Decisions

| Decision | Alternative | Reason |
|----------|------------|--------|
| `api` and `bot` as separate services | Single service | Clean architecture, API can be used independently |
| Webhook instead of long polling | Long polling | Static IP available, webhook is faster and more professional |
| PostgreSQL | SQLite | Production experience, scalability |
| Provider pattern for LLM and STT | Hardcoded service | Switch between cloud/local via `.env`, no code changes |
| Anthropic as default LLM | Ollama | Reliable JSON output, cheap enough at ~$1/mo |
| Groq as default STT | faster-whisper | Free tier, no GPU needed on server |
| Feature module registry | Monolithic routers | Adding a module touches only its own files |
| Claude Haiku | Claude Sonnet | Cheaper for simple parsing tasks |
| aiogram | python-telegram-bot | Best async library for Telegram |
| Multi-user (public bot) | Single-user whitelist | More useful product, better for portfolio |
| ElevenLabs TTS | OpenAI TTS, Google TTS | Best voice quality, free tier available |
| Inline keyboard for voice reply | Auto-send voice always | User chooses — saves API costs, better UX |
| MkDocs + GitHub Pages | README only | Beautiful docs site, auto-deployed |

---

## Progress

- [x] Base FastAPI CRUD
- [x] PostgreSQL + Alembic migrations (users + tasks tables)
- [ ] Modular feature architecture (api/modules + bot/modules)
- [ ] Provider layer (LLMProvider + STTProvider abstractions)
- [ ] Anthropic provider implementation
- [ ] Groq STT provider implementation
- [ ] Ollama provider implementation
- [ ] faster-whisper provider implementation
- [ ] Multi-user support (auto-register on first message)
- [ ] Docker Compose
- [ ] nginx + Let's Encrypt
- [ ] aiogram bot + webhook
- [ ] Inline keyboard buttons
- [ ] ElevenLabs integration (TTS)
- [ ] News module
- [ ] GitHub Actions CI/CD
- [ ] Watchtower auto-deploy
- [ ] MkDocs setup + GitHub Pages
- [ ] README + documentation