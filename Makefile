# Docker
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api

# Database
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(name)"

rollback:
	alembic downgrade -1

# Testing
test:
	pytest api/tests/

lint:
	ruff check .
