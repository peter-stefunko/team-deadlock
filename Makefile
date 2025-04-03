.PHONY: help

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
start: ## Start docker-compose in development mode
	@docker compose -f ./docker/docker-compose.yml up

build: ## Build docker-compose in development mode
	@docker compose -f ./docker/docker-compose.yml build

logs: ## Show logs from all docker containers
	@docker compose -f ./docker/docker-compose.yml logs -f

down: ## Stop all development docker containers
	@docker compose -f ./docker/docker-compose.yml down

db-delete: down ## Delete development database
	@docker volume rm deadlock_db-data

clean: ## Clean all dev images
	@docker images | grep 'deadlock-be' | awk '{print $$3}' | xargs -r docker image rm -f
	@echo "Cleaned all dev images"
