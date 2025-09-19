# Clinical Copilot - Frontend to Backend Connection

This document explains how the Clinical Copilot frontend is connected to the Python backend services.

## Architecture Overview

```
┌─────────────────┐     HTTP API     ┌─────────────────┐
│                 │    (port 5000)   │                 │
│  Next.js        │ ←──────────────→ │  Flask          │
│  Frontend       │                  │  Backend        │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
                                              │
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │  ChromaDB       │
                                     │  Vector Store   │
                                     │                 │
                                     └─────────────────┘
```

## Services Connected

### 1. Patient Data API
- **Endpoint**: `/api/patient`
- **Source**: `src/patient_data.json`
- **Frontend**: `lib/api.ts` → `fetchPatient()`

### 2. Medical Records APIs
- **Conditions**: `/api/conditions` → `fetchConditions()`
- **Medications**: `/api/medications` → `fetchMedications()`
- **Allergies**: `/api/allergies` → `fetchAllergies()`
- **Lab Results**: `/api/labs` → `fetchLabResults()`
- **Vitals**: `/api/vitals` → `fetchVitals()`

### 3. Clinical Search API
- **Endpoint**: `/api/search` (POST)
- **Source**: `src/search.py` + ChromaDB vector database
- **Frontend**: `lib/api.ts` → `searchPatientData()`
- **Features**: 
  - Vector similarity search
  - Semantic search of patient data
  - Filterable by data type

### 4. Recommendations API
- **Endpoint**: `/api/recommendations` (POST)
- **Source**: Clinical decision support logic
- **Frontend**: `lib/api.ts` → `getRecommendations()`

## Configuration Files

### Backend Configuration (`src/.env`)
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
VECTOR_DB_DIR=./patient_vectors
API_HOST=localhost
API_PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Configuration (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
```

## Setup Instructions

### Automated Setup (Windows)
1. Run `setup.bat` to install all dependencies
2. Run `start.bat` to start both services

### Manual Setup
1. **Backend Setup**:
   ```bash
   cd src
   python -m venv venv
   venv\Scripts\activate.bat  # Windows
   pip install -r requirements.txt
   python embed.py  # Initialize vector database
   python app.py    # Start Flask server
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev      # Start Next.js development server
   ```

## API Endpoints Reference

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/health` | GET | Health check | `{status, message}` |
| `/api/patient` | GET | Patient demographics | `Patient` object |
| `/api/conditions` | GET | Medical conditions | `Condition[]` |
| `/api/medications` | GET | Medications | `Medication[]` |
| `/api/allergies` | GET | Allergies | `Allergy[]` |
| `/api/labs` | GET | Lab results | `LabResult[]` |
| `/api/vitals` | GET | Vital signs | `Vital[]` |
| `/api/search` | POST | Vector search | `SearchResponse` |
| `/api/recommendations` | POST | Clinical recommendations | `Recommendation[]` |

## Data Flow

1. **Patient Data Loading**: 
   - `patient_data.json` → Flask app → API endpoints → Frontend components

2. **Vector Search**:
   - User query → Frontend → `/api/search` → ChromaDB → Similarity results → Frontend

3. **Real-time Updates**:
   - Frontend polls APIs for data updates
   - CORS enabled for local development

## Dependencies

### Backend (`src/requirements.txt`)
- `flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - CORS support
- `chromadb==0.4.18` - Vector database
- `sentence-transformers==2.2.2` - Text embeddings
- `python-dotenv==1.0.0` - Environment variables

### Frontend (package.json)
- Next.js 14+ with TypeScript
- Tailwind CSS + shadcn/ui components
- React hooks for state management

## Testing the Connection

1. Start both services
2. Visit `http://localhost:3000`
3. Use the search functionality to test backend connection
4. Check browser network tab for API calls to `http://localhost:5000`

## Troubleshooting

### Backend Issues
- Ensure Python virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify vector database exists: `python embed.py`
- Check Flask server logs for errors

### Frontend Issues
- Ensure Node.js dependencies are installed: `npm install`
- Check browser console for API connection errors
- Verify environment variables are loaded
- Test direct API endpoints: `curl http://localhost:5000/api/health`

### Connection Issues
- Verify both servers are running on correct ports
- Check CORS configuration in Flask app
- Ensure firewall allows local connections
- Test with browser dev tools network tab

## Development Notes

- Hot reloading enabled for both frontend and backend
- API changes require backend restart
- Vector database updates require running `embed.py`
- New patient data requires updating `patient_data.json`