.PHONY: help start stop restart logs rebuild test clean

help:
	@echo "Content Service Management Commands:"
	@echo "  make start    - Start all services"
	@echo "  make stop     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - Show logs"
	@echo "  make rebuild  - Rebuild and start"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"

start:
	docker-compose up -d

stop:
	docker-compose down

restart: stop start

logs:
	docker-compose logs -f

rebuild:
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

test:
	docker-compose exec content-service pytest tests/ -v

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f