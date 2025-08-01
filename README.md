# Legal document analysis platform

Upload documents. Extract metadata. With the help of query find out needed info from files.

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
cp .env.example .env
# !! Add OpenAI API key to .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

Create `backend/.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=true
MAX_FILE_SIZE=52428800
```

## Features

- Upload PDF/DOCX documents
- AI metadata extraction (agreement type, jurisdiction, industry)
- Natural language document queries
- Analytics dashboard with charts
- Background document processing


## API Endpoints

- `POST /api/v1/upload` - Upload documents
- `POST /api/v1/query` - Natural language queries
- `GET /api/v1/dashboard` - Analytics data
- `GET /api/v1/documents` - List documents