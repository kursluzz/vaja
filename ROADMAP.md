# vaja — Roadmap

> Planned milestones, upcoming features, and nice-to-have ideas.
> Concrete work items are tracked in [GitHub Issues](../../issues).

---

## Milestones

### v0.1 — Database & Basic CRUD API ⏳ 63%
- [x] Project structure setup
- [x] Docker Compose — db service
- [x] SQLAlchemy async setup
- [x] Users table migration
- [x] Tasks table migration
- [x] FastAPI app + health check
- [x] Modular architecture refactor
- [ ] Tasks CRUD endpoints
- [ ] Users endpoints
- [ ] Docker Compose — api service
- [ ] Manual testing via Swagger UI

### v0.2 — AI Integration
- [ ] Provider layer (LLMProvider / STTProvider abstractions)
- [ ] Anthropic Claude Haiku provider
- [ ] Groq Whisper STT provider
- [ ] Parse natural language → structured task (`POST /tasks/parse`)
- [ ] Prioritize task list (`POST /tasks/prioritize`)
- [ ] Daily digest (`POST /tasks/summarize`)
- [ ] Suggest subtasks (`POST /tasks/suggest`)

### v0.3 — CI/CD & Deployment
- [ ] GitHub Actions — lint + test + build
- [ ] Push Docker image to GHCR
- [ ] Watchtower auto-deploy on server

### v0.4 — SSL & Certbot
- [ ] nginx reverse proxy config
- [ ] Let's Encrypt SSL via certbot
- [ ] Auto-renewal setup

### v0.5 — Telegram Bot
- [ ] aiogram bot setup (webhook mode)
- [ ] Auto-register user on first message
- [ ] Text message handlers (tasks module)
- [ ] Inline keyboard buttons
- [ ] Callback handlers

### v0.6 — Speech to Text
- [ ] Groq Whisper STT provider implementation
- [ ] Voice message handler in bot
- [ ] faster-whisper local provider (alternative)

### v0.7 — Text to Speech
- [ ] ElevenLabs TTS integration
- [ ] `🔊 Listen` inline button
- [ ] Voice reply on button press

---

## Planned Features

### Local AI (v0.8)
- [ ] Ollama LLM provider implementation
- [ ] Switch between Anthropic / Ollama via `LLM_PROVIDER` env var
- [ ] Docker Compose profile for Ollama service
- [ ] faster-whisper STT provider implementation

### News Module (v0.9)
- [ ] RSS feed aggregation (feedparser)
- [ ] User interest configuration (`/news setup`)
- [ ] Daily news digest (`/news today`)
- [ ] Background news collection (APScheduler)
- [ ] News module bot handlers

---

## Nice to Have

### More Feature Modules
- **Events** — local events aggregator (concerts, movies, meetups) based on user preferences. Agent collects data 1-2 times per day. User can ask to read events aloud, receive a digest via Telegram or email, or filter by category
- **Places** — interesting places to visit aggregator (historical sites, nature, parks, kid-friendly attractions) based on user location and preferences. Agent enriches data with descriptions, ratings, and directions
- **Habits** — daily habit tracker with streaks
- **Notes** — quick voice/text notes with AI tagging
- **Reminders** — time-based reminders with Telegram notifications
- **Finance** — expense tracking via voice input

### AI Enhancements
- Recurring task detection ("every Monday")
- Smart due date inference from natural language
- Task completion patterns and productivity insights
- Multi-language voice input

### UX
- Telegram Web App (mini app) for visual task management
- Pagination for long task lists
- Task sharing between users
- Export tasks to CSV / iCal

### Infrastructure
- Metrics endpoint (`/metrics`) for Prometheus
- Structured JSON logging
- Rate limiting per user
- Backup script for PostgreSQL data