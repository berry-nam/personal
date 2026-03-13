.PHONY: dev prod deploy down logs db-shell etl etl-newstapa etl-likms lint test build clean

# ── Development ───────────────────────────────────────────────────────────────

dev: ## Start all services in dev mode
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

prod: ## Start all services in production mode
	COMPOSE_TARGET=prod docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

deploy: ## Deploy with Caddy HTTPS reverse proxy
	docker compose -f docker-compose.yml -f deploy/docker-compose.deploy.yml up --build -d

down: ## Stop all services
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

db-shell: ## Open psql shell
	docker compose exec db psql -U kracc -d kracc

# ── ETL ───────────────────────────────────────────────────────────────────────

etl: ## Run ETL sync_all flow
	docker compose exec etl-worker python -m flows.sync_all

etl-historical: ## Sync historical politicians (terms 17-21)
	docker compose exec etl-worker python -c "import asyncio; from flows.sync_historical_politicians import sync_historical_politicians; asyncio.run(sync_historical_politicians())"

etl-newstapa: ## Scrape asset declarations from Newstapa
	docker compose exec etl-worker python -c "import asyncio; from flows.scrape_newstapa import scrape_newstapa; asyncio.run(scrape_newstapa())"

etl-likms: ## Scrape per-member votes from LIKMS
	docker compose exec etl-worker python -c "import asyncio; from flows.scrape_likms_votes import scrape_likms_votes; asyncio.run(scrape_likms_votes())"

# ── Quality ───────────────────────────────────────────────────────────────────

lint: ## Lint backend + ETL + frontend
	cd backend && ruff check . && ruff format --check .
	cd etl && ruff check . && ruff format --check .
	cd frontend && npx tsc --noEmit

test: ## Run backend tests
	cd backend && pytest -v --tb=short

build: ## Build frontend for production
	cd frontend && npx vite build

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean: ## Stop services and remove volumes
	docker compose down -v

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
