# =====================================================
# AI Service Makefile
# 用于快速执行常用命令
# =====================================================

.PHONY: help install dev test lint format docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Start development server"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make clean       - Clean up generated files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --port 8002

worker:
	celery -A app.scheduler.celery_app worker --loglevel=info

beat:
	celery -A app.scheduler.celery_app beat --loglevel=info

test:
	pytest tests/ -v

lint:
	flake8 app/
	mypy app/

format:
	black app/
	isort app/

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/

