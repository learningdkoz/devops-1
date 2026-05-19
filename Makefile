# Makefile — единая точка входа для локального запуска тех же команд,
# что крутятся в CI. Удобно для разработчика и для воспроизводимости.

PY ?= .venv/bin/python
PIP ?= .venv/bin/pip
IMAGE ?= devops-demo:dev

.PHONY: help venv install lint format type test cov sec audit run docker-build docker-run clean

help: ## показать список целей
	@awk 'BEGIN{FS=":.*?## "}/^[a-zA-Z_-]+:.*?## /{printf "  %-15s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

venv: ## создать виртуалку
	python3 -m venv .venv

install: ## поставить рантайм + dev-зависимости
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

lint: ## ruff check (CI-04)
	$(PY) -m ruff check app tests

format: ## ruff format
	$(PY) -m ruff format app tests

type: ## mypy (CI-05)
	$(PY) -m mypy app

test: ## юнит + интеграционные тесты (CI-10)
	$(PY) -m pytest

cov: test ## алиас — тесты + покрытие (CI-11)

sec: ## bandit — SAST по питону (CI-06)
	$(PY) -m bandit -q -r app

audit: ## pip-audit — SCA (CI-08)
	$(PY) -m pip_audit -r requirements-dev.txt || true

run: ## запустить сервис локально
	$(PY) -m app.server

docker-build: ## собрать образ (CI-15)
	docker build -t $(IMAGE) .

docker-run: docker-build ## собрать и запустить контейнер
	docker run --rm -p 8080:8080 $(IMAGE)

clean: ## выкинуть кэши
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov build dist *.egg-info
