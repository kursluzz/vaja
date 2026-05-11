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
- **Anthropic Claude Haiku** — task parsing, prioritization, digest, subtasks
- **Groq Whisper** — voice message transcription (speech-to-text)
- **ElevenLabs** — text-to-speech, bot replies with voice messages
- Structured outputs from Claude via JSON mode

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
│   ├── main.py
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic models (request/response validation)
│   ├── routers/            # endpoints
│   │   ├── tasks.py        # tasks CRUD
│   │   └── ai.py           # AI endpoints
│   ├── services/
│   │   └── claude.py       # Anthropic integration
│   └── database.py
├── bot/                    # aiogram Telegram bot
│   ├── main.py
│   ├── handlers/
│   │   ├── tasks.py        # text message handlers
│   │   ├── voice.py        # voice message handlers
│   │   └── callbacks.py    # inline keyboard button handlers
│   └── services/
│       ├── groq.py         # Whisper speech-to-text
│       └── elevenlabs.py   # ElevenLabs text-to-speech
├── alembic/                # DB migrations
├── nginx/
│   └── nginx.conf
├── docs/                   # MkDocs documentation (deployed to vaja.dev/docs)
│   ├── index.md            # overview
│   ├── installation.md     # how to install
│   ├── configuration.md    # .env setup
│   ├── self-hosting.md     # deploy to your server
│   ├── usage.md            # how to use the bot
│   └── api.md              # API endpoints reference
├── mkdocs.yml              # MkDocs config
├── Makefile                # dev shortcuts (make up, make migrate, make test)
├── docker-compose.yml
├── docker-compose.dev.yml  # for local development
├── .env.example
├── README.md
├── ARCHITECTURE.md         # this file
└── ROADMAP.md
```

---

## API Endpoints

### Tasks CRUD
```
GET    /tasks          — list tasks
POST   /tasks          — create task
GET    /tasks/{id}     — get single task
PUT    /tasks/{id}     — update task
DELETE /tasks/{id}     — delete task
```

### AI Endpoints
```
POST /ai/parse         — parse natural language → task
POST /ai/prioritize    — prioritize task list
POST /ai/summarize     — daily digest
POST /ai/suggest       — suggest subtasks for a task
```

---

## External Services & Costs

| Service | Usage | Cost |
|---------|-------|------|
| Telegram Bot API | Webhook, messages | Free |
| Anthropic Claude Haiku | AI parsing and analysis | ~$0.50-1/mo |
| Groq Whisper | Voice transcription (STT) | Free (28k sec/mo) |
| ElevenLabs | Text-to-speech (TTS) | Free (10k chars/mo) |
| Let's Encrypt | SSL certificate | Free |
| GHCR | Docker images | Free |
| GitHub Actions | CI/CD | Free (open source) |

**Total: ~$1/month**

---

## Architecture Decisions

| Decision | Alternative | Reason |
|----------|------------|--------|
| `api` and `bot` as separate services | Single service | Clean architecture, API can be used independently |
| Webhook instead of long polling | Long polling | Static IP available, webhook is faster and more professional |
| PostgreSQL | SQLite | Production experience, scalability |
| Groq Whisper | OpenAI Whisper | Faster, cheaper, free tier available |
| Claude Haiku | Claude Sonnet | Cheaper for simple parsing tasks |
| aiogram | python-telegram-bot | Best async library for Telegram |
| Multi-user (public bot) | Single-user whitelist | More useful product, better for portfolio |
| ElevenLabs TTS | OpenAI TTS, Google TTS | Best voice quality, free tier available |
| Inline keyboard for voice reply | Auto-send voice always | User chooses — saves API costs, better UX |
| MkDocs + GitHub Pages | README only, GitHub Wiki | Beautiful docs site, auto-deployed, professional for portfolio |
| GitHub Issues + Projects | Jira, Notion, Linear | Free, everything in one place with the code |

---

## Progress

- [ ] Base FastAPI CRUD
- [ ] PostgreSQL + Alembic migrations (users + tasks tables)
- [ ] Multi-user support (auto-register on first message)
- [ ] Docker Compose
- [ ] nginx + Let's Encrypt
- [ ] aiogram bot + webhook
- [ ] Inline keyboard buttons
- [ ] Groq Whisper integration (STT)
- [ ] ElevenLabs integration (TTS)
- [ ] Claude AI endpoints
- [ ] GitHub Actions CI/CD
- [ ] Watchtower auto-deploy
- [ ] MkDocs setup + GitHub Pages
- [ ] GitHub Issues + Projects setup
- [ ] README + documentation
