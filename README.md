# vaja 🎤

> **Voice AI Assistant** — A Telegram bot for task management with voice input and AI intelligence powered by Claude.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)

---

## What is this

**vaja** is a personal AI task assistant you control through Telegram. Just type or send a voice message — vaja understands, structures, and saves the task. Claude analyzes priorities, suggests subtasks, and generates a daily digest.

## Features

- 🎤 **Voice input** — record a voice message, bot transcribes and adds the task
- 🧠 **AI parsing** — "buy milk tomorrow by 6pm" → structured task
- 📊 **Smart priorities** — Claude prioritizes your task list
- 📋 **Daily digest** — summary of today's tasks in one command
- 💡 **Subtasks** — AI breaks down a big task into steps
- 🔒 **Self-hosted** — all your data stays at home
- 🧩 **Modular** — plug-and-play features (tasks, news, and more)

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + PostgreSQL |
| AI logic | Claude (Anthropic) or Ollama (local) |
| Voice | Whisper via Groq or faster-whisper (local) |
| Interface | Telegram (aiogram) |
| Deployment | Docker Compose + nginx |
| SSL | Let's Encrypt (certbot) |
| CI/CD | GitHub Actions + Watchtower |

## Status

vaja is in early development. The tasks CRUD API works; the Telegram bot, AI
and voice features are in progress. See the [milestones](https://github.com/kursluzz/vaja/milestones)
and [ROADMAP.md](ROADMAP.md). Server deployment instructions will be added with
v0.3 (CI/CD & Deployment).

## Development

```bash
git clone https://github.com/kursluzz/vaja.git
cd vaja
make setup      # deps, local config, database, migrations
make api-run    # http://localhost:8000/docs
```

Requirements: Docker and [uv](https://docs.astral.sh/uv/). See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full setup guide, debugging, and
how to submit changes.

## Usage

```
# Text input
You: buy milk tomorrow by 6pm
Bot: ✅ Task added — buy milk, 📅 tomorrow 18:00

# Voice input
You: 🎤 [voice message]
Bot: ✅ Task added from voice message

# Commands
/tasks          — list all tasks
/today          — tasks for today
/ai prioritize  — prioritize task list
/ai digest      — daily digest
/ai suggest     — suggest subtasks
/done [id]      — mark as complete
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## CI/CD

Push to `main` → GitHub Actions builds Docker image → pushes to GHCR → Watchtower on the server automatically updates containers.

## License

MIT — use it, fork it, improve it.
