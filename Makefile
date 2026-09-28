# Setup
setup:
	uv sync --all-groups
	test -f .env || cp .env.example .env
	test -f docker-compose.override.yml || \
		cp docker-compose.override.example.yml docker-compose.override.yml
	docker compose up -d --wait db
	uv run alembic upgrade head

# Docker
up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps

api-logs:
	docker compose logs -f api

db-up:
	docker compose up -d db

db-logs:
	docker compose logs db

db-connect:
	docker compose exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# Database
migration:
	uv run alembic revision --autogenerate -m "$(name)"

migrate:
	uv run alembic upgrade head

rollback:
	uv run alembic downgrade -1

# Code quality
lint:
	uv run ruff format .
	uv run ruff check --fix .

lint-check:
	uv run ruff format --check .
	uv run ruff check .


# Testing
test:
	uv run pytest api/tests/

uv-sync:
	uv sync --all-groups

# Local API
api-run:
	uv run uvicorn api.main:app --reload

-include Makefile.local  # For personal stuff