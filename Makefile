.PHONY: up down infra logs test test-db test-api test-ml test-ui lint typecheck migrate seed smoke-train train eval pin worker-gpu-native

# One command for students: full stack.
up:
	docker compose --profile gpu up -d --build

down:
	docker compose --profile gpu down

# Just the stateful services (for local development and tests).
infra:
	docker compose up -d postgres redis minio

logs:
	docker compose logs -f --tail=200

migrate:
	uv run alembic -c packages/core/alembic.ini upgrade head

seed:
	uv run python -m ledgerlens_core.seed

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy packages apps

test: lint typecheck test-db test-api test-ml

test-db:
	uv run pytest tests/db

test-api:
	uv run pytest tests/api

test-ml:
	uv run pytest tests/ml

test-ui:
	cd apps/web && pnpm exec playwright test

smoke-train:
	uv run python -m ledgerlens_worker.cli train --profile smoke

train:
	uv run python -m ledgerlens_worker.cli train --profile $(or $(PROFILE),demo) $(if $(MODEL),--model $(MODEL),)

eval:
	uv run python -m ledgerlens_worker.cli evaluate --model-version $(MV)

pin:
	uv run python -m ledgerlens_worker.cli pin --model-version $(MV)

# Fallback when GPU passthrough into Docker is unavailable on this machine.
worker-gpu-native:
	uv run celery -A ledgerlens_worker.app worker -Q gpu -l INFO --concurrency=1 --pool=solo
