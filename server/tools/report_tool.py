import json
from typing import Dict, Any, List

class ReportTool:
    @staticmethod
    def compile_report_prompt(
        filters: Dict[str, Any],
        metrics: Dict[str, Any],
        sql_query: str,
        news: List[Dict[str, Any]]
    ) -> str:
        """
        Assembles metrics, SQL query structure, and news list into a clean structured string
        that will be passed as context to the LLM.
        """
        
        metrics_str = (
            f"- Total Cases Analyzed: {metrics.get('total_cases', 0)}\n"
            f"- Mortality Rate: {metrics.get('mortality_rate', 0.0) * 100:.2f}%\n"
            f"- ICU Admission Rate: {metrics.get('icu_rate', 0.0) * 100:.2f}%\n"
            f"- Hospitalized Vaccination Rate (% of inpatients vaccinated against COVID-19): "
            f"{metrics.get('hospitalized_vaccination_rate', 0.0) * 100:.2f}%\n"
            f"  [NOTE: This is NOT a population-level rate. It reflects vaccination status among "
            f"hospitalized SRAG cases only (VACINA_COV field). No IBGE population denominators are used.]\n"
            f"- Case Growth/Increase Rate (last 30 days vs previous 30 days): {metrics.get('case_increase_rate', 0.0) * 100:.2f}%\n"
        )

        # Format news
        news_str = ""
        if news:
            for idx, article in enumerate(news, 1):
                news_str += (
                    f"{idx}. Title: {article.get('title')}\n"
                    f"   Date: {article.get('date')}\n"
                    f"   URL: {article.get('url')}\n"
                    f"   Summary: {article.get('summary')}\n\n"
                )
        else:
            news_str = "No recent news found.\n"

        context_prompt = f"""
### Epidemiological Report Context Data

**Analysis Parameters:**
- Start Date: {filters.get('start_date', 'N/A')}
- End Date: {filters.get('end_date', 'N/A')}
- Region/State (UF): {filters.get('uf', 'All States (BR)')}

**Calculated Metrics (Deterministic):**
{metrics_str}

**DuckDB Query Executed:**
```sql
{sql_query}
```

**Recent News/Contextual Factors:**
{news_str}
"""
        return context_prompt
