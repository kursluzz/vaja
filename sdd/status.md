# Status

Phase: 1 - Discovery (in progress)
Next: discovery interview (users, languages, time zones, API exposure), then Phase 2 (requirements for v0.2-v0.7)

```text
- [x] Phase 0: Baseline            → spec.md §0 (approved 2026-09-29, PR #24)
- [~] Phase 1: Discovery           (short — product idea is mostly known)
- [ ] Phase 2: Requirements & scope
- [ ] Phase 3: Architecture & ADRs (convert ARCHITECTURE.md decision table to ADRs)
- [ ] Phase 4: Feature specs       (AI parse/prioritize/summarize/suggest, bot flows, voice)
- [ ] Phase 5: Readiness check
- [ ] Phase 6: Implementation plan
- [ ] Phase 7: Implementation
```

## Confirmed requirements

_None formally confirmed yet._ The existing behaviour is documented in
[spec.md §0](spec.md#0-baseline--current-state-as-of-2026-09-28-commit-0094969).

## Assumptions

- A-001: The API is internal only: the bot reaches it over the Docker network, and nginx exposes only the bot webhook.
- A-002: Single deployment and one Telegram bot, but many users (multi-user public bot per ARCHITECTURE.md).
- A-003: The feature-module layout (`api/modules/<name>/`) is the intended structure, and CLAUDE.md's `routers/` + `services/` layout is outdated.

## Open questions

- Q-001 [CRITICAL] **API authentication.** `/tasks` trusts a `user_id` query param, so anyone who can reach the API can read or modify any user's tasks. Should the API stay internal-only (A-001), require a shared service token from the bot, or both?
- Q-002 **Where the AI endpoints live.** CLAUDE.md says `/ai/parse` etc. ROADMAP.md says `/tasks/parse` etc.
- Q-003 **Where STT lives.** CLAUDE.md says `bot/services/groq.py`, ARCHITECTURE.md says the provider layer in `api`. ROADMAP.md schedules the Groq STT provider in both v0.2 and v0.6.
- Q-004 **Where the LLM integration lives.** CLAUDE.md says "Claude only in `api/services/claude.py`", ARCHITECTURE.md says an `LLMProvider` abstraction with Anthropic and Ollama.
- Q-005 **Task fields.** CLAUDE.md describes `priority` as `int` and does not mention `category`. The code uses `low/medium/high` and has `category`. Is the code right?
- Q-006 **Update semantics.** `PUT /tasks/{id}` behaves like PATCH (partial update). Keep PUT, rename it to PATCH, or make PUT a full replacement?
- Q-007 **User identity on the API.** Tasks use the internal `users.id`, but the bot only knows `telegram_user_id`, so it needs an extra lookup on every request. Should `/tasks` accept the Telegram ID instead?
- Q-008 **Bot transport.** ARCHITECTURE.md specifies webhook mode. Should local dev use long polling?
- Q-009 **News module.** ARCHITECTURE.md lists `news` under "Current Modules", but it is planned for v0.9. Move it to "planned"?

## Constraints

- Self-hosted on one server with Docker Compose. Deployment is `git push` → GHCR → Watchtower.
- Cost: Claude Haiku only for routine AI work. Use free tiers (Groq, ElevenLabs) where possible.
- Stack is fixed: Python 3.12, FastAPI, PostgreSQL 16, aiogram 3.
- Open source (MIT), and contributors are expected to use GitHub Issues.

## Decisions

The existing decisions are recorded in the table in `ARCHITECTURE.md` → "Architecture Decisions".
They are not yet converted to ADRs (Phase 3).

## Risks

- ~~R-001: The API does not start on `main` (D-001), and migrations are broken (D-002).~~ Fixed in #22 / PR #23.
- R-002: No tests exist, so the CI gate planned for v0.3 has nothing to run.
- R-003: The same facts (structure, endpoints, schema) are described in CLAUDE.md, ARCHITECTURE.md and ROADMAP.md, and the copies already disagree (Q-002 to Q-005, Q-009).

## Tasks

_Created in Phase 6._ Candidate fixes from the baseline, which don't depend on the spec:
D-003 (verify), D-004 (+ migration), D-005 (add first test), D-006. D-001 and D-002 are fixed (#22).
