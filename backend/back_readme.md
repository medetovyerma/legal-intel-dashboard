# Legal Intel Dashboard - Backend

Backend in Fastapi , LLM model - Openai 4o
## Setup

1. **Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run server:**
```bash
uvicorn app.main:app --reload
```

Server runs on http://localhost:8000

## Environment Variables

```bash
# Required for AI features
OPENAI_API_KEY=your_api_key_here

# Optional settings
DEBUG=true
MAX_FILE_SIZE=52428800  # 50MB
DATABASE_URL=sqlite:///./legal_documents.db
UPLOAD_DIR=./uploads
```

## API Documentation

Interactive docs available at http://localhost:8000/docs

**Main endpoints:**
- `POST /api/v1/upload` - Upload documents
- `POST /api/v1/query` - Query documents
- `GET /api/v1/dashboard` - Get statistics
- `GET /health` - Health check

## Architecture

```
app/
├── api/           # API endpoints
├── core/          # Configuration & database
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
└── services/      # Business logic
```


## Testing

```bash
pytest
pytest --cov=app tests/
```


## Dependencies

- FastAPI 
- SQLAlchemy
- OpenAI 
- PyPDF2
- python-docx 