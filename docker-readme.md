# Docker Setup

## Quick Start

1. **Setup environment:**
```bash
cp .env.docker .env
# Edit .env and add OpenAI API key (optional)
```

2. **Start application:**
```bash
docker-compose up -d
```

3. **Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

## Data Storage

- Documents: `./backend/uploads/`
- Database: `./backend/legal_documents.db`

Both are automatically created and persisted on your local machine.