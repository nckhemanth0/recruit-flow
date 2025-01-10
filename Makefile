SHELL := /bin/bash
COMPOSE := docker compose

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down --remove-orphans

backend-dev:
	python -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm run dev -- --host
