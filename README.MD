# HealthCareAI

An AI-powered healthcare reporting system that generates epidemiological reports on Severe Acute Respiratory Syndrome (SRAG) in Brazil by combining structured DATASUS SIVEP-Gripe data with health news. Built using FastAPI + LangGraph + DuckDB on the backend and React + Vite + TypeScript + Tailwind CSS v3 on the frontend.

## Project Structure

```text
HealthCareAI/
├── app/                  # React Frontend (Vite, TypeScript, Tailwind v3)
├── server/               # FastAPI Backend
│   ├── agent/            # LangGraph agent definitions (state, nodes, graph)
│   ├── api/              # API endpoints
│   ├── database/         # DuckDB connections
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic (DataLoader, LLM provider registry)
│   ├── tools/            # Agent tools (SQL, metrics, news, charts)
│   ├── utils/            # Shared utilities (logger, mock data generator)
│   └── requirements.txt  # Python requirements
├── data/                 # Raw and cleaned data
└── .env                  # Configuration keys
```

## Setup & Running

### 1. Requirements

Ensure you have:
- **Node.js** v20+ / npm
- **Python** 3.12+

### 2. Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate it:
   - On Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - On Linux/macOS: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r server/requirements.txt
   ```
4. Copy the environment template in the root `.env` file and configure your API Keys (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.).
5. Run the development server:
   ```bash
   python -m uvicorn server.main:app --reload
   ```
   The backend will be running at `http://localhost:8000`.

### 3. Frontend Setup

1. Install frontend packages:
   ```bash
   cd app
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The web application will open at `http://localhost:5173`.

## Mock Data Generator
If you want to re-generate the mock DATASUS dataset, run:
```bash
python server/utils/generate_mock_data.py
```
This generates raw patient records in `data/raw/srag.csv` which are cleaned on server start and exported to the DuckDB-compatible `data/processed/cleaned.parquet` file.
