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
- Matplotlib
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

## Daabase Decisions

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

                  Report Endpoint

                         │

                         ▼

                 LangGraph Orchestrator

          ┌──────────────┼──────────────┐

          ▼              ▼              ▼

      SQL Tool      News Tool      Chart Tool

          │              │              │

          ▼              ▼              ▼

      DuckDB        News Search      Pandas

                                         │

                                         ▼

                                   Matplotlib

                         │

                         ▼

                    LLM Summarization

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

```
Receive Request

↓

Validate Input

↓

Determine Required Information

↓

Execute SQL Tool

↓

Compute Metrics

↓

Generate Charts

↓

Search News

↓

Send structured context to LLM

↓

Generate Report

↓

Return Report
```

---

# Required Metrics

The report must contain:

- Increase rate of cases
- Mortality rate
- ICU occupancy rate
- Vaccination rate

These metrics must be calculated directly from the healthcare dataset.

---

# Charts

Two charts are required.

## Daily Cases

Last 30 days

---

## Monthly Cases

Last 12 months

Charts should be generated using Pandas and Matplotlib.

The frontend will display the resulting images or receive structured data to render using Recharts.

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
    "icu_rate": 0.62
}
```

---

## Chart Tool

Responsibilities:

Generate:

- Daily chart
- Monthly chart

Output:

```python
{
    "daily_chart": "...",
    "monthly_chart": "..."
}
```

---

## News Tool

Responsibilities:

Search recent news.

Return:

- title
- date
- url
- summary

No AI summarization occurs here.

---

## Report Tool

Responsible for assembling all collected information into a structured prompt for the LLM.

The LLM only writes.

It never computes.

---

# LangGraph Nodes

Suggested nodes:

```
Input Node

↓

Validation Node

↓

SQL Node

↓

Metrics Node

↓

Charts Node

↓

News Node

↓

LLM Report Node

↓

Output Node
```

Each node should have exactly one responsibility.

---

# Backend Folder Structure

```
backend/

    app/

        agent/

            graph.py
            nodes.py
            state.py
            prompts.py

        api/

            report.py

        tools/

            sql_tool.py
            metrics_tool.py
            news_tool.py
            chart_tool.py
            report_tool.py

        services/

            data_loader.py
            report_service.py

        database/

            duckdb.py

        models/

            report.py
            metrics.py

        utils/

            logger.py
            dates.py

        logs/

        main.py
```

---

# Frontend Structure

```
frontend/

    src/

        components/

        pages/

        hooks/

        services/

        types/

        lib/

        assets/
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

        srag.csv

    processed/

        cleaned.parquet
```

Raw files are immutable.

Processed files contain cleaned datasets.

---

# Documentation

```
docs/

    architecture.pdf

    diagrams/

    screenshots/
```

The repository must include:

- architecture diagram
- explanation of the Agent
- explanation of each Tool
- data flow

---

# Logging & Auditability

Every Agent execution should be logged.

Suggested log:

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

## POST /report

Returns

```
{
    metrics,
    charts,
    explanation,
    news,
    execution_log
}
```

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

# Error Handling

Tools should never crash the Agent.

Instead, they should return structured errors.

Example:

```
{
    "success": false,
    "reason": "No vaccination data found."
}
```

The Agent decides how to proceed.

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