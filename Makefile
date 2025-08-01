# Legal Intel Dashboard

.PHONY: help start stop logs build clean

help:
	@echo "Available commands:"
	@echo "  make start  - Start application"
	@echo "  make stop   - Stop application"  
	@echo "  make logs   - View logs"
	@echo "  make build  - Rebuild containers"
	@echo "  make clean  - Clean everything"

start:
	@if [ ! -f .env ]; then cp .env.docker .env; echo "Created .env file. Add your OpenAI API key."; fi
	docker-compose up -d
	@echo "Started successfully:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"

stop:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose up -d --build

clean:
	docker-compose down -v
	docker system prune -f