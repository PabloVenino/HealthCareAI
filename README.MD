# HealthCareAI

> **PoC** — AI-powered epidemiological reporting system for Severe Acute Respiratory Syndrome (SRAG) in Brazil.

An AI Agent capable of generating structured epidemiological reports by combining structured healthcare data from **Open DATASUS SIVEP-Gripe** with real-time health news. Built using **FastAPI + LangGraph + DuckDB** on the backend and **React + Vite + TypeScript + Tailwind CSS v3** on the frontend.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Workflow](#agent-workflow)
3. [Tool Descriptions](#tool-descriptions)
4. [Data Flow](#data-flow)
5. [Dataset — SRAG SIVEP-Gripe](#dataset--srag-sivep-gripe)
6. [Metric Definitions](#metric-definitions)
7. [Project Structure](#project-structure)
8. [Setup & Running](#setup--running)
9. [Design Principles](#design-principles)

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              React Frontend                 │
│   (Vite · TypeScript · Tailwind · shadcn)   │
└──────────────────────┬──────────────────────┘
                       │  POST /api/report
                       ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│         (Python 3.12 · Uvicorn)             │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │       LangGraph Orchestrator          │  │
│  │  (Sequential state-machine pipeline)  │  │
│  │                                       │  │
│  │  validate → sql → metrics → charts    │  │
│  │       → news → llm_report             │  │
│  └──────┬──────────┬──────────┬──────────┘  │
│         │          │          │             │
│    SQL Tool   Metrics   Chart Tool          │
│         │    Tool  │          │             │
│         ▼          ▼          ▼             │
│      DuckDB    Pandas     Pandas            │
│    (srag view)         (JSON records)       │
│                              │              │
│                    React Recharts           │
│                   (renders in browser)      │
│                                             │
│    News Tool ──────► Google News RSS        │
│                                             │
│    Report Tool ────► LLM Provider           │
│                     (Gemini / OpenAI /      │
│                      Anthropic / Mock)      │
└─────────────────────────────────────────────┘
                       │
          Structured JSON response
          (metrics · charts · report ·
           news · execution_log)
```

The architecture follows a **strict separation of concerns**:

| Layer | Responsibility |
|-------|----------------|
| Frontend | Display — no business logic |
| FastAPI | HTTP contract, request validation, error handling middleware |
| LangGraph | Orchestration, state management |
| Tools | Single-purpose, deterministic computation |
| DuckDB | Analytical SQL over the SRAG dataset |
| LLM | Narrative generation only — never computes |

> **Core principle**: The LLM never invents numbers. Every metric is calculated deterministically in Python and passed to the LLM as pre-computed context. The LLM only writes the narrative and explains correlations.

---

## Agent Workflow

The LangGraph agent is a **sequential state machine**. Each node has exactly one responsibility and appends to the shared `execution_log` for full auditability.

```
Request received
      │
      ▼
┌─────────────┐
│  Validate   │  Extract date range and UF filter from structured filters.
│    Node     │  Apply defaults (last 180 days, all states) if not provided.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  SQL Node   │  Build a deterministic SELECT query and execute it
│             │  against the DuckDB `srag` view. Returns raw rows.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Metrics    │  Calculate epidemiological indicators from DuckDB directly
│    Node     │  (mortality rate, ICU rate, vaccination rate, case growth).
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Charts     │  Query DuckDB and build Pandas DataFrames:
│    Node     │  · Daily cases (last 30 days)
│             │  · Monthly cases (last 12 months)
│             │  Returns JSON records — Recharts renders in browser.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  News Node  │  Search Google News RSS for recent SRAG/Gripe/COVID-19
│             │  articles. Returns structured error if feed is unavailable.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ LLM Report  │  Assemble metrics + SQL + news into a structured prompt.
│    Node     │  Call LLM provider to write the markdown narrative report.
└──────┬──────┘
       │
       ▼
  Final Response
  (metrics · charts · explanation · news · execution_log)
```

---

## Tool Descriptions

### `sql_tool.py` — SQL Tool

**Responsibility**: Execute read-only SQL queries against the DuckDB `srag` view.

- Implements a blocklist guardrail rejecting any query containing `DROP`, `DELETE`, `INSERT`, `UPDATE`, `CREATE`, `ALTER`, or `TRUNCATE`.
- Returns structured rows or a `{"success": false, "error": "..."}` dict — never raises.
- The query is passed through to the API response for full auditability.

### `metrics_tool.py` — Metrics Tool

**Responsibility**: Calculate the four required epidemiological metrics deterministically from the database.

| Metric | Formula | Notes |
|--------|---------|-------|
| `mortality_rate` | `deaths / total_cases` | Based on `EVOLUCAO = '2'` (death by SRAG) |
| `icu_rate` | `icu_admissions / total_cases` | Based on `UTI = '1'` |
| `hospitalized_vaccination_rate` | `vaccinated / total_cases` | Share of **inpatients** with COVID vaccination (see [Metric Definitions](#metric-definitions)) |
| `case_increase_rate` | `(cases_A - cases_B) / cases_B` | Compares last 30 days vs. previous 30 days |

Never generates explanations. Returns structured dicts only.

### `chart_tool.py` — Chart Tool

**Responsibility**: Query DuckDB and return time-series data as serialized Pandas DataFrames for the frontend to render.

- **Daily chart data**: Case counts for each of the last 30 days relative to `end_date`.
- **Monthly chart data**: Aggregated case counts per calendar month for the last 12 months.
- Returns structured JSON records — no image files are generated server-side.
- The React frontend renders these datasets as interactive charts using **Recharts**.
- Returns `{"daily_chart": [{"DT_NOTIFIC": ..., "case_count": ...}], "monthly_chart": [{"month": ..., "case_count": ...}]}`.

### `news_tool.py` — News Tool

**Responsibility**: Retrieve recent contextual health news without AI summarization.

- Queries Google News RSS for queries like `"SRAG" OR "Gripe" OR "COVID-19"`.
- Returns a list of `{title, date, url, summary}` objects (summary is sourced from the RSS feed).
- On failure, returns a structured `{"success": false, "reason": "..."}` dict — **no mock/fabricated articles are ever returned**.
- The news is used **only** to help the LLM explain metric trends — not to compute any value.

### `report_tool.py` — Report Tool

**Responsibility**: Assemble all collected data into a structured prompt context string for the LLM.

- Formats metrics with clear labels (including the `hospitalized_vaccination_rate` caveat).
- Embeds the executed SQL query for transparency.
- Lists news articles with title, date, URL, and summary.
- Returns a plain-text string — the LLM receives this as its user prompt.

---

## Data Flow

```
CSV (srag.csv)
      │
      ▼  DataLoader.ensure_data_ready()
Pandas cleaning
  · parse DT_NOTIFIC, DT_SIN_PRI dates
  · normalize EVOLUCAO, UTI, VACINA_COV to string codes
  · drop rows with null notification date
      │
      ▼
DuckDB view `srag`
(in-memory from cleaned.parquet)
      │
      ├──► SQL Tool ──► raw row count / sample rows
      │
      ├──► Metrics Tool ──► mortality_rate, icu_rate,
      │                     hospitalized_vaccination_rate,
      │                     case_increase_rate
      │
      └──► Chart Tool ──► daily/monthly Pandas DataFrames
                          (serialized as JSON records)

JSON chart data ──► React frontend ──► Recharts renders charts in browser

Google News RSS ──► News Tool ──► list of news articles (or structured error)

All above ──► Report Tool ──► structured context string
                                    │
                                    ▼
                              LLM Provider
                          (generates narrative only)
                                    │
                                    ▼
                        Markdown Epidemiological Report
```

---

## Dataset — SRAG SIVEP-Gripe

### What is it?

The **SIVEP-Gripe** (Sistema de Informação de Vigilância Epidemiológica da Gripe) dataset is the Brazilian Ministry of Health's official registry of severe acute respiratory syndrome hospitalizations. It is published under Open DATASUS and covers all notified SRAG inpatient cases from 2009 onwards.

The current production dataset (`INFLUD24`) contains **~165,000+ rows** and **~120 columns** per year. The full historical series spans 2019–2026.

### Why DuckDB?

DuckDB was chosen as the analytical database because:

- **Embedded** — no separate database server required.
- **Columnar** — extremely fast analytical aggregations over 100k+ rows.
- **CSV/Parquet native** — reads `srag.csv` and `.parquet` files directly via SQL.
- **Pandas-compatible** — results are returned as DataFrames or dicts with zero friction.
- **Serverless** — single `.db` file, perfect for a PoC.

### Column Selection Rationale

The full SIVEP-Gripe dataset contains ~120 columns. This application uses a curated subset focused on analytical, diagnostic, and outcome fields. The complete mapping is documented in [`data/data-dictionary.md`](data/data-dictionary.md).

**Core columns used by the AI:**

| Column | Description | Used For |
|--------|-------------|----------|
| `DT_NOTIFIC` | Notification date | Time-series filtering and charting |
| `SG_UF_NOT` | Brazilian state (UF) | Geographic filtering |
| `EVOLUCAO` | Patient outcome (`1`=cure, `2`=death) | Mortality rate |
| `UTI` | ICU admission (`1`=yes) | ICU rate |
| `VACINA_COV` | COVID vaccination status (`1`=yes) | Hospitalized vaccination rate |
| `CLASSI_FIN` | Final etiological classification | Agent breakdown |

**Deliberately excluded:**
- Patient names, CPF, birth dates — PII, never exposed.
- Hospital names, bed numbers — operational, not analytical.
- ~60 administrative/metadata columns — not relevant for epidemiology metrics.

---

## Metric Definitions

### Mortality Rate
```
mortality_rate = deaths_by_SRAG / total_hospitalized_cases
```
Counts rows where `EVOLUCAO = '2'` (death attributed to SRAG).

### ICU Admission Rate
```
icu_rate = icu_admissions / total_hospitalized_cases
```
Counts rows where `UTI = '1'`.

### Hospitalized Vaccination Rate
```
hospitalized_vaccination_rate = vaccinated_inpatients / total_hospitalized_cases
```
> ⚠️ **Important caveat**: This metric measures the **proportion of hospitalized SRAG cases** who had previously received a COVID-19 vaccine (`VACINA_COV = '1'`). It is **NOT** a population-level vaccination rate. It does not use IBGE population denominators. A high value simply reflects overall vaccine coverage in Brazil and should not be interpreted as "vaccines cause hospitalization."
>
> A more accurate name for this metric is *"taxa de vacinados entre os internados"* (vaccination prevalence among inpatients).

### Case Increase Rate
```
case_increase_rate = (cases_last_30_days - cases_prev_30_days) / cases_prev_30_days
```
Compares the most recent 30-day window against the preceding 30-day window relative to `end_date`.

---

## Project Structure

```text
HealthCareAI/
├── app/                          # React Frontend (Vite, TypeScript, Tailwind v3)
│   ├── Dockerfile
│   └── src/
│       ├── App.tsx               # Main application component
│       ├── components/           # UI components (MetricCard, ChartsPanel, NewsPanel, etc.)
│       ├── services/             # API client and TypeScript types
│       └── utils/                # Shared frontend utilities
│
├── server/                       # FastAPI Backend
│   ├── Dockerfile
│   ├── agent/
│   │   ├── graph.py              # LangGraph StateGraph definition
│   │   ├── nodes.py              # One function per pipeline node
│   │   ├── orchestrator.py       # Entry point to run the compiled graph
│   │   ├── prompts.py            # LLM system and user prompt templates
│   │   └── state.py              # AgentState TypedDict
│   ├── api/
│   │   └── report.py             # POST /api/report endpoint
│   ├── database/
│   │   └── duckdb.py             # DuckDB singleton client
│   ├── models/
│   │   ├── metrics.py            # EpidemiologicalMetrics Pydantic model
│   │   └── report.py             # ReportRequest / ReportResponse Pydantic models
│   ├── services/
│   │   ├── data_loader.py        # CSV cleaning pipeline, DuckDB view registration
│   │   └── llm_service.py        # LLM provider registry (Gemini, OpenAI, Anthropic, Mock)
│   ├── tools/
│   │   ├── sql_tool.py           # Read-only SQL execution with guardrails
│   │   ├── metrics_tool.py       # Epidemiological metric calculation
│   │   ├── chart_tool.py         # DuckDB → Pandas chart data (JSON records for Recharts)
│   │   ├── news_tool.py          # Google News RSS search
│   │   └── report_tool.py        # LLM context assembly
│   ├── utils/
│   │   └── logger.py             # Shared logger factory
│   ├── static/charts/            # Reserved directory (charts returned as JSON, not saved as PNG)
│   ├── main.py                   # FastAPI app factory, middleware, and startup hooks
│   └── requirements.txt
│
├── data/
│   ├── raw/srag.csv              # Source dataset (immutable)
│   ├── processed/cleaned.parquet # Cleaned dataset (auto-generated on startup)
│   └── data-dictionary.md        # Column reference for all SRAG fields
│
├── docs/                         # Documentation and diagrams
├── architecture.pdf              # System architecture diagram
├── architecture.png              # Architecture diagram (PNG export)
├── docker-compose.yml            # Orchestrates backend + frontend containers
├── .env                          # API keys (never commit to version control)
├── .env.example                  # Template for required environment variables
├── .gitignore
└── README.MD
```

---

## Setup & Running

### Option A — Docker (Recommended)

The easiest way to run the full stack. Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# Copy and configure your environment variables first
cp .env.example .env
# Edit .env to add your LLM API key

# Build and start both services
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

### Option B — Manual Setup

#### Requirements

- **Node.js** v20+ / npm
- **Python** 3.12+

#### 1. Environment Variables

Copy the template and configure your API keys:

```bash
cp .env.example .env
```

Required keys (at least one LLM key):

```env
LLM_PROVIDER=gemini           # gemini | openai | anthropic | mock
API_KEY=your_key_here
MODEL=LLM_Model_goes_here
```

> The `mock` provider generates a deterministic placeholder report without calling any LLM — useful for development and testing.

#### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r server/requirements.txt

# Start the development server
python -m uvicorn server.main:app --reload
```

The backend will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
cd app
npm install
npm run dev
```

The web application will open at `http://localhost:5173`.

---

## Design Principles

This project prioritizes **AI Engineering best practices** over maximizing LLM usage:

| Principle | Implementation |
|-----------|---------------|
| **LLM as narrator, not calculator** | All metrics computed in Python; LLM only writes narrative |
| **Determinism** | SQL + Pandas calculations are reproducible given the same inputs |
| **Auditability** | Every node appends to `execution_log`; SQL query is exposed in the UI |
| **Guardrails** | SQL blocklist, LLM prompt constraints, structured error returns |
| **Transparency** | Raw SQL and news sources are displayed in the frontend |
| **No PII exposure** | Only aggregated statistics reach the LLM and API response |
| **Graceful degradation** | Every tool returns `{"success": false, "reason": "..."}` on failure — no fabricated fallbacks |
| **Provider abstraction** | LLM backend is swappable via `LLM_PROVIDER` env var; mock fallback for tests |
