.PHONY: help build up down restart logs shell test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker compose build

up: ## Start all services
	docker compose up -d
	@echo "API is running at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"

up-with-nginx: ## Start with Nginx reverse proxy
	docker compose --profile with-nginx up -d
	@echo "API is running behind Nginx at http://localhost"

up-with-cache: ## Start with Redis cache
	docker compose --profile with-cache up -d

up-full: ## Start with all optional services
	docker compose --profile with-nginx --profile with-cache up -d

down: ## Stop all services
	docker compose down

down-clean: ## Stop and remove volumes
	docker compose down -v

restart: ## Restart all services
	docker compose restart

logs: ## Show logs (follow)
	docker compose logs -f

logs-api: ## Show API logs only
	docker compose logs -f api

shell: ## Open shell in API container
	docker compose exec api /bin/bash

shell-root: ## Open root shell in API container
	docker compose exec -u root api /bin/bash

ps: ## Show running containers
	docker compose ps

test: ## Run tests inside container
	docker compose exec api pytest

health: ## Check API health
	@curl -s http://localhost:8000/health | jq .

clean: ## Remove stopped containers and unused images
	docker compose down
	docker system prune -f

rebuild: ## Rebuild and restart
	docker compose down
	docker compose build --no-cache
	docker compose up -d

dev: ## Run in development mode with auto-reload
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up