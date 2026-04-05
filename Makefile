BACKEND_PYTHON := backend/.venv/bin/python
BACKEND_RUFF   := backend/.venv/bin/ruff
BACKEND_MYPY   := backend/.venv/bin/mypy

# ── Help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Backend ───────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run backend unit tests
	$(BACKEND_PYTHON) -m pytest backend/tests/ -v

.PHONY: test-q
test-q: ## Run backend unit tests (quiet)
	$(BACKEND_PYTHON) -m pytest backend/tests/ -q

.PHONY: lint
lint: ## Lint backend (ruff) + frontend (eslint)
	$(BACKEND_RUFF) check backend/app/
	cd frontend && npm run lint --silent

.PHONY: lint-fix
lint-fix: ## Auto-fix lint issues (ruff + eslint)
	$(BACKEND_RUFF) check --fix backend/app/
	$(BACKEND_RUFF) format backend/app/

.PHONY: typecheck
typecheck: ## Type-check backend (mypy) + frontend (tsc)
	$(BACKEND_MYPY) backend/app/ --ignore-missing-imports
	cd frontend && npx tsc -b --noEmit

.PHONY: check
check: lint typecheck test ## Run all checks (lint + typecheck + tests)

# ── Docker ────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Build Docker images
	docker compose build

.PHONY: up
up: ## Start all services (detached)
	docker compose up -d

.PHONY: up-build
up-build: ## Build and start all services
	docker compose up --build

.PHONY: down
down: ## Stop all services
	docker compose down

.PHONY: logs
logs: ## Tail logs from all services
	docker compose logs -f

.PHONY: dev
dev: ## Start all services with hot-reloading (dev mode)
	docker compose -f docker-compose.dev.yml up --build

.PHONY: dev-d
dev-d: ## Start all services with hot-reloading, detached (dev mode)
	docker compose -f docker-compose.dev.yml up --build -d

.PHONY: dev-down
dev-down: ## Stop dev services
	docker compose -f docker-compose.dev.yml down
