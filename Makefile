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
	docker compose exec db psql -U taskuser -d taskdb

# Database
migration:
	alembic revision --autogenerate -m "$(name)"

migrate:
	alembic upgrade head

rollback:
	alembic downgrade -1

# Code quality
lint:
	ruff check --fix .
	ruff format .

lint-check:
	ruff check .
	ruff format --check .

# Testing
test:
	pytest api/tests/

uv-sync:
	uv sync --all-groups