# Legal Intel Dashboard - Frontend

React TypeScript frontend with modern UI components.

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

Frontend runs on http://localhost:3000

## Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for prod
npm run preview    # Preview production build
npm run type-check # TypeScript type checking
```

## Project Structure

```
src/
├── components/    # Reusable UI components
├── pages/         # Page components
├── services/      # API communication
├── types/         # TypeScript definitions
└── App.tsx        # Main application
```

## Pages

- **Upload** (`/`) - Document upload interface
- **Query** (`/query`) - Natural language search
- **Dashboard** (`/dashboard`) - Analytics and charts

## Components

- **UploadZone** - Drag-and-drop file upload
- **QueryInput** - Natural language input
- **ResultsTable** - Dynamic query results
- **DashboardView** - Charts and statistics

## API Integration

Backend API base URL configured in `src/services/api.ts`:
- Development: `http://localhost:8000/api/v1`
- Production: `/api/v1`
