# HealthCareAI - Project Guidelines

## Project Overview

This project is a Proof of Concept (PoC) for an AI-powered healthcare reporting system.

The objective is to build an AI Agent capable of generating epidemiological reports about Severe Acute Respiratory Syndrome (SRAG) by combining structured healthcare data from Open DATASUS with real-time news.

The AI should **not** simply answer questions using an LLM. Instead, it must orchestrate multiple tools to retrieve data, compute metrics, generate visualizations, search for supporting news, and finally produce a transparent report.

The solution is intentionally designed following AI Engineering best practices instead of being a simple CRUD application.

---

# Core Principles

This project prioritizes:

- Clean Architecture
- AI Agent Orchestration
- Transparency
- Auditability
- Guardrails
- Reproducibility
- Separation of Concerns
- Extensibility

Every component should have one clear responsibility.

---

# Technology Stack

## Backend

- Python 3.12+
- FastAPI
- LangGraph
- LangChain
- DuckDB
- Pandas
- Pydantic

## Frontend

- React
- TypeScript
- Vite
- TanStack Query
- React Router
- Recharts
- TailwindCSS
- shadcn/ui

---

## Database Decisions

DuckDB was chosen because:

- Embedded database
- Single file
- Extremely fast analytical queries
- Reads CSV directly
- Excellent integration with Pandas
- Better suited for analytical workloads than SQLite, for example

Example:

```sql
SELECT *
FROM read_csv_auto("srag.csv");
```

No import process is required.

---

# High-Level Architecture

```
                   React Frontend

                         │

                         ▼

                  FastAPI Backend

                         │

               POST /api/report Endpoint

                         │

                         ▼

                 LangGraph Orchestrator

          ┌──────────────┼──────────────┐

          ▼              ▼              ▼

      SQL Tool      News Tool      Chart Tool

          │              │              │

          ▼              ▼              ▼

      DuckDB        News Search      Pandas

    (srag view)                    (JSON records)

                                        │

                                        ▼

                                 React Recharts
                             (renders in browser)

                         │

                         ▼

                    LLM Summarization
              (Gemini / OpenAI / Anthropic / Mock)

                         │

                         ▼

                  Final Structured Report
```

---

# Agent Philosophy

The LLM is **not** responsible for calculations.

The LLM should only:

- summarize
- explain
- correlate
- write

Every metric must come from deterministic code.

The LLM never invents numbers.

---

# Agent Workflow

The LangGraph agent is a **sequential state machine** — no branching or conditional edges.

```
Receive Request

↓

Validate Input (apply defaults: last 180 days, all states)

↓

Execute SQL Tool (deterministic SELECT against DuckDB srag view)

↓

Compute Metrics (mortality rate, ICU rate, vaccination rate, case growth)

↓

Generate Charts (daily last 30 days · monthly last 12 months)

↓

Search News (Google News RSS — returns structured error on failure, never fabricates)

↓

Send structured context to LLM

↓

Generate Report (LLM writes narrative only)

↓

Return Report
```

---

# Required Metrics

The report must contain:

- Increase rate of cases
- Mortality rate
- ICU occupancy rate
- Vaccination rate (hospitalized inpatients only)

These metrics must be calculated directly from the healthcare dataset.

---

# Charts

Two charts are required.

## Daily Cases

Last 30 days

---

## Monthly Cases

Last 12 months

Charts are built by querying DuckDB with Pandas and returning the result as JSON records (`to_dict(orient="records")`).

The React frontend receives this structured data and renders the charts using **Recharts** — no image files are generated on the server.

---

# News Search

The Agent must retrieve recent news about SRAG.

The news is **not** used to compute metrics.

Instead, it is used to explain why the observed metrics may have changed.

Example:

Metric:

ICU Occupancy increased by 12%.

Explanation:

Recent influenza outbreaks reported by national news agencies may explain the increase.

**Guardrail**: If the RSS feed is unavailable, the tool returns a structured failure dict. It never falls back to fabricated or hardcoded mock articles.

---

# Tool Design

The Agent communicates only through tools.

Never place business logic inside prompts.

---

## SQL Tool

Responsibilities:

- Query DuckDB
- Return structured results
- Never generate explanations

Guardrail: Rejects any query containing `DROP`, `DELETE`, `INSERT`, `UPDATE`, `CREATE`, `ALTER`, or `TRUNCATE`.

Output:

```python
{
    "rows": ...
}
```

---

## Metrics Tool

Responsibilities:

- Calculate epidemiological metrics
- Validate missing data
- Return deterministic values

Output:

```python
{
    "mortality_rate": 0.034,
    "icu_rate": 0.62,
    "hospitalized_vaccination_rate": 0.71,
    "case_increase_rate": 0.12
}
```

---

## Chart Tool

Responsibilities:

Query DuckDB and build Pandas DataFrames:

- Daily data (last 30 days)
- Monthly data (last 12 months)

Returns JSON records. The React frontend renders these with Recharts.
No PNG files are written to disk.

Output:

```python
{
    "daily_chart": [{"DT_NOTIFIC": "2024-01-01", "case_count": 42}, ...],
    "monthly_chart": [{"month": "2024-01", "case_count": 1230}, ...]
}
```

---

## News Tool

Responsibilities:

Search recent news via Google News RSS.

Return:

- title
- date
- url
- summary

No AI summarization occurs here.

On failure: returns `{"success": false, "reason": "...", "news": []}`.

Never fabricates news.

---

## Report Tool

Responsible for assembling all collected information into a structured prompt for the LLM.

The LLM only writes.

It never computes.

---

# LangGraph Nodes

Implemented nodes (in execution order):

```
validate        → validate_node

↓

sql_query       → sql_node

↓

compute_metrics → metrics_node

↓

generate_charts → charts_node

↓

search_news     → news_node

↓

generate_report → llm_report_node
```

Each node has exactly one responsibility and appends a log entry to `execution_log`.

---

# Backend Folder Structure

```
server/

    Dockerfile

    main.py                  # FastAPI app factory, CORS, error middleware, startup hooks

    requirements.txt

    agent/

        graph.py             # LangGraph StateGraph definition
        nodes.py             # One function per pipeline node
        orchestrator.py      # Entry point — compiles and runs the graph
        prompts.py           # LLM system and user prompt templates
        state.py             # AgentState TypedDict

    api/

        report.py            # POST /api/report endpoint

    database/

        duckdb.py            # DuckDB singleton client

    models/

        metrics.py           # EpidemiologicalMetrics Pydantic model
        report.py            # ReportRequest / ReportResponse Pydantic models

    services/

        data_loader.py       # CSV cleaning pipeline, DuckDB view registration
        llm_service.py       # LLM provider registry (Gemini, OpenAI, Anthropic, Mock)

    tools/

        sql_tool.py          # Read-only SQL execution with DML blocklist guardrail
        metrics_tool.py      # Epidemiological metric calculation
        chart_tool.py        # Matplotlib chart generation
        news_tool.py         # Google News RSS search (no mock fallback)
        report_tool.py       # LLM context assembly

    utils/

        logger.py            # Shared logger factory

    static/

        charts/              # Reserved directory (unused — charts returned as JSON)
```

---

# Frontend Structure

```
app/

    Dockerfile

    src/

        App.tsx              # Main application component

        components/          # UI components (MetricCard, ChartsPanel, NewsPanel,
                             #   ExecutionLogPanel, SqlViewer, ReportNarrative, etc.)

        services/            # API client and TypeScript types

        utils/               # Shared frontend utilities

        assets/              # Static assets
```

Frontend responsibilities:

- Request reports
- Display metrics
- Display charts
- Display explanations
- Display sources
- Display agent execution logs

No business logic should exist in React.

---

# Data Folder

```
data/

    raw/

        srag.csv             # Source dataset (immutable)

    processed/

        cleaned.parquet      # Auto-generated on startup by DataLoader
```

Raw files are immutable.

Processed files contain cleaned datasets and are regenerated automatically.

`cleaned.parquet` and transient DuckDB files are excluded from version control via `.gitignore`.

---

# Documentation

```
docs/                        # Documentation folder

architecture.pdf             # System architecture diagram (project root)
architecture.png             # Architecture diagram PNG export (project root)
```

The repository includes:

- Architecture diagram
- Explanation of the Agent
- Explanation of each Tool
- Data flow

---

# Logging & Auditability

Every Agent execution is logged via the `execution_log` field in the API response.

Each LangGraph node appends an entry when it completes. The log is returned to the frontend and displayed in the UI.

```
Request received

↓

Validation completed

↓

SQL Tool executed

↓

Metrics calculated

↓

Charts generated

↓

News searched

↓

LLM called

↓

Report completed
```

This satisfies transparency and governance requirements.

---

# Guardrails

The Agent must never:

- fabricate metrics
- fabricate SQL
- expose patient-level data
- invent news
- answer using assumptions

If information is unavailable:

Return that it is unavailable.

Never hallucinate.

---

# Sensitive Data

Although Open DATASUS is public, patient-level information must never be exposed.

Only aggregated statistics should be returned.

The report should never display:

- patient identifiers
- birth dates
- addresses
- names

---

# Prompt Engineering

Prompts should only be responsible for:

- explanation
- summarization
- report writing

Prompts should never:

- calculate values
- execute business rules
- infer statistics

---

# API Design

## POST /api/report

Returns

```json
{
    "metrics": {},
    "charts": {},
    "explanation": "",
    "news": [],
    "execution_log": []
}
```

---

# Error Handling

Tools should never crash the Agent.

Instead, they should return structured errors.

Example:

```json
{
    "success": false,
    "reason": "No vaccination data found."
}
```

The Agent decides how to proceed.

FastAPI also exposes a global error-handling middleware that catches unhandled exceptions and returns consistent `{"detail": "..."}` JSON responses to the client.

---

# Deployment

The project ships with a `docker-compose.yml` at the project root that orchestrates both services:

```
docker compose up --build
```

| Service  | Port | Notes                          |
|----------|------|-------------------------------|
| backend  | 8000 | FastAPI + Uvicorn              |
| frontend | 5173 | Vite dev server (hot reload)   |

---

# Coding Standards

- Type hints everywhere
- Pydantic models
- Small functions
- Single Responsibility Principle
- Avoid global state
- Dependency Injection when appropriate
- Prefer composition over inheritance

---

# Future Improvements

Possible future enhancements:

- RAG over healthcare documentation
- Vector database
- Multiple specialized Agents
- Human-in-the-loop approval
- Streaming responses
- Authentication
- Historical report comparison
- Scheduled report generation
- Multi-region support

---

# Development Philosophy

The goal of this project is **not** to maximize LLM usage.

The goal is to demonstrate good AI Engineering practices.

The LLM should be treated as one component inside a deterministic system.

Business logic belongs in Python.

Reasoning belongs in the Agent.

Narrative belongs in the LLM.

This separation makes the system more reliable, auditable, maintainable, and production-ready.