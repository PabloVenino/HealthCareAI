import re
from datetime import datetime, timedelta
from typing import Dict, Any
from server.agent.state import AgentState
from server.tools.sql_tool import SQLTool
from server.tools.metrics_tool import MetricsTool
from server.tools.chart_tool import ChartTool
from server.tools.news_tool import NewsTool
from server.tools.report_tool import ReportTool
from server.services.llm_service import get_llm_provider
from server.agent.prompts import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT_TEMPLATE

def validate_node(state: AgentState) -> Dict[str, Any]:
    """
    Validates input query, extracts date filters and UF (state) code.
    Sets default dates if not provided.
    """
    logs = state.get("execution_log", [])
    logs.append("Validation Node: Starting analysis validation")
    
    query = state.get("query", "")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    uf = None
    
    # Regex parsing for UF (e.g., SP, RJ, MG)
    uf_match = re.search(r'\b(SP|RJ|MG|RS|PR|BA|AM|DF)\b', query, re.IGNORECASE)
    if uf_match:
        uf = uf_match.group(1).upper()
        
    # Regex parsing for dates (YYYY-MM-DD)
    date_matches = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', query)
    if len(date_matches) >= 2:
        sorted_dates = sorted(date_matches)
        start_date = sorted_dates[0]
        end_date = sorted_dates[1]
    elif len(date_matches) == 1:
        end_date = date_matches[0]
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (end_dt - timedelta(days=180)).strftime("%Y-%m-%d")

    explicit_filters = state.get("filters", {})
    if explicit_filters:
        if "start_date" in explicit_filters and explicit_filters["start_date"]:
            start_date = explicit_filters["start_date"]
        if "end_date" in explicit_filters and explicit_filters["end_date"]:
            end_date = explicit_filters["end_date"]
        if "uf" in explicit_filters and explicit_filters["uf"]:
            uf = explicit_filters["uf"]

    logs.append(f"Validation Node: Cleaned parameters -> Start: {start_date}, End: {end_date}, State (UF): {uf}")
    
    return {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "uf": uf or "ALL"
        },
        "validation_error": None,
        "execution_log": logs
    }
    

def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Generates and executes SQL query against DuckDB.
    """
    logs = state.get("execution_log", [])
    logs.append("SQL Node: Generating query for DuckDB")
    
    filters = state.get("filters", {})
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    uf = filters.get("uf")
    
    where_clause = f"DT_NOTIFIC BETWEEN '{start_date}' AND '{end_date}'"
    if uf and uf != "ALL":
        where_clause += f" AND SG_UF_NOT = '{uf}'"
        
    sql_query = f"SELECT * FROM srag WHERE {where_clause} ORDER BY DT_NOTIFIC ASC;"
    
    logs.append(f"SQL Node: Executing query: {sql_query}")
    tool = SQLTool()
    res = tool.run_query(sql_query)
    
    if not res.get("success"):
        logs.append(f"SQL Node: Error running query: {res.get('error')}")
        return {
            "sql_query": sql_query,
            "sql_results": [],
            "validation_error": f"SQL query failed: {res.get('error')}",
            "execution_log": logs
        }
    
    rows = res.get("rows", [])
    logs.append(f"SQL Node: Query executed successfully. Retrieved {len(rows)} cases.")
    
    return {
        "sql_query": sql_query,
        "sql_results": rows,
        "execution_log": logs
    }


def metrics_node(state: AgentState) -> Dict[str, Any]:
    """
    Calculates epidemiological metrics from database.
    """
    logs = state.get("execution_log", [])
    logs.append("Metrics Node: Initiating calculations")
    
    filters = state.get("filters", {})
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    uf = filters.get("uf")
    
    tool = MetricsTool()
    res = tool.calculate_metrics(start_date, end_date, uf)
    
    if not res.get("success"):
        logs.append(f"Metrics Node: Error calculating metrics: {res.get('error')}")
        default_metrics = {
            "total_cases": 0,
            "total_deaths": 0,
            "total_icu": 0,
            "total_vaccinated": 0,
            "mortality_rate": 0.0,
            "icu_rate": 0.0,
            "hospitalized_vaccination_rate": 0.0,
            "case_increase_rate": 0.0
        }
        return {
            "metrics": default_metrics,
            "execution_log": logs
        }
    
    logs.append(
        f"Metrics Node: Calculations completed. Mortality Rate: {res.get('mortality_rate')}, "
        f"ICU Rate: {res.get('icu_rate')}, Case Growth: {res.get('case_increase_rate')}"
    )
    return {
        "metrics": res,
        "execution_log": logs
    }


def charts_node(state: AgentState) -> Dict[str, Any]:
    """
    Generates daily and monthly Matplotlib plots.
    """
    logs = state.get("execution_log", [])
    logs.append("Charts Node: Generating trend visualizations")
    
    filters = state.get("filters", {})
    end_date = filters.get("end_date")
    uf = filters.get("uf")
    
    tool = ChartTool()
    res = tool.generate_charts(end_date, uf)
    
    if not res.get("success"):
        logs.append(f"Charts Node: Error creating charts: {res.get('error')}")
        return {
            "charts": {"daily_chart": None, "monthly_chart": None},
            "execution_log": logs
        }
        
    logs.append(f"Charts Node: Visualizations saved to: {res.get('daily_chart')} & {res.get('monthly_chart')}")
    return {
        "charts": res,
        "execution_log": logs
    }


def news_node(state: AgentState) -> Dict[str, Any]:
    """
    Searches contextual health news.
    """
    logs = state.get("execution_log", [])
    logs.append("News Node: Searching recent articles about SRAG/Gripe/COVID-19")
    
    tool = NewsTool()
    res = tool.search_news("SRAG")
    
    news_list = res.get("news", [])
    logs.append(f"News Node: Found {len(news_list)} recent health reports/articles.")
    return {
        "news": news_list,
        "execution_log": logs
    }


def llm_report_node(state: AgentState) -> Dict[str, Any]:
    """
    Assembles prompt and calls the LLM provider to write the final markdown report.
    """
    logs = state.get("execution_log", [])
    logs.append("LLM Report Node: Preparing prompt context")
    
    filters = state.get("filters", {})
    metrics = state.get("metrics", {})
    sql_query = state.get("sql_query", "")
    news = state.get("news", [])
    
    context_data = ReportTool.compile_report_prompt(filters, metrics, sql_query, news)
    
    user_prompt = REPORT_USER_PROMPT_TEMPLATE.format(context_data=context_data)
    
    logs.append("LLM Report Node: Dispatching request to LLM provider")
    try:
        provider = get_llm_provider()
        report_text = provider.generate_text(
            system_prompt=REPORT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2
        )
        logs.append("LLM Report Node: Relatório epidemiológico gerado com sucesso.")
    except Exception as e:
        logs.append(f"LLM Report Node: Error calling LLM: {str(e)}")
        report_text = (
            f"## Falha na Geração do Relatório\n\n"
            f"Ocorreu um erro ao chamar o modelo de linguagem: {str(e)}\n\n"
            f"### Dados do Período:\n"
            f"- Total de Casos: {metrics.get('total_cases', 0)}\n"
            f"- Taxa de Mortalidade: {metrics.get('mortality_rate', 0.0) * 100:.2f}%\n"
            f"- Taxa de Ocupação de UTI: {metrics.get('icu_rate', 0.0) * 100:.2f}%\n"
        )
        
    return {
        "report": report_text,
        "execution_log": logs
    }
