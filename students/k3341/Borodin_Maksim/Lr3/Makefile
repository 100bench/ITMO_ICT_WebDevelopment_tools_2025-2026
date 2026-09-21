COMPOSE ?= docker compose

.PHONY: run up down logs ps

run: up

up:
	$(COMPOSE) up --build -d
	$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps
