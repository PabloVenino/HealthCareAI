from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from server.database.duckdb import get_db_client

class MetricsTool:
    def __init__(self):
        self.db = get_db_client()

    def calculate_metrics(self, start_date: str, end_date: str, uf: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates case increase rate, mortality rate, ICU rate, and the
        hospitalized vaccination rate for a given period and optional state.

        NOTE — hospitalized_vaccination_rate:
            This metric represents the proportion of *hospitalized SRAG cases*
            in the selected period who had received a COVID-19 vaccine
            (VACINA_COV = '1'). It is NOT a population-level vaccination rate;
            it does not use population denominators from IBGE or any external
            source. A high value means many hospitalised patients were vaccinated,
            which is expected given high vaccination coverage in the population
            and does not imply that vaccination caused hospitalization.
        """
        try:
            where_clause = "WHERE DT_NOTIFIC BETWEEN ? AND ?"
            params = [start_date, end_date]
            if uf and uf.strip() and uf.upper() != "ALL":
                where_clause += " AND SG_UF = ?"
                params.append(uf.upper().strip())

            query = f"""
                SELECT 
                    COUNT(*) as total_cases,
                    SUM(CASE WHEN EVOLUCAO = '2' THEN 1 ELSE 0 END) as total_deaths,
                    SUM(CASE WHEN UTI = '1' THEN 1 ELSE 0 END) as total_icu,
                    SUM(CASE WHEN VACINA_COV = '1' THEN 1 ELSE 0 END) as total_vaccinated
                FROM srag
                {where_clause}
            """
            
            results = self.db.execute_query(query, tuple(params))
            if not results or results[0]["total_cases"] == 0:
                return {
                    "success": False,
                    "error": "No cases found in the selected period and region to compute metrics."
                }
            
            metrics = results[0]
            total_cases = metrics["total_cases"]
            total_deaths = metrics["total_deaths"] or 0
            total_icu = metrics["total_icu"] or 0
            total_vaccinated = metrics["total_vaccinated"] or 0

            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            mid_dt = end_dt - timedelta(days=30)
            start_compare_dt = end_dt - timedelta(days=60)

            str_end = end_dt.strftime("%Y-%m-%d")
            str_mid = mid_dt.strftime("%Y-%m-%d")
            str_start_comp = start_compare_dt.strftime("%Y-%m-%d")

            # Period A: [mid_dt + 1, end_dt]
            # Period B: [start_compare_dt, mid_dt]
            period_a_query = f"SELECT COUNT(*) as cnt FROM srag WHERE DT_NOTIFIC > ? AND DT_NOTIFIC <= ?"
            period_a_params = [str_mid, str_end]
            period_b_query = f"SELECT COUNT(*) as cnt FROM srag WHERE DT_NOTIFIC >= ? AND DT_NOTIFIC <= ?"
            period_b_params = [str_start_comp, str_mid]

            if uf and uf.strip() and uf.upper() != "ALL":
                period_a_query += " AND SG_UF_NOT = ?"
                period_a_params.append(uf.upper().strip())
                period_b_query += " AND SG_UF_NOT = ?"
                period_b_params.append(uf.upper().strip())

            cases_a = self.db.execute_query(period_a_query, tuple(period_a_params))[0]["cnt"] or 0
            cases_b = self.db.execute_query(period_b_query, tuple(period_b_params))[0]["cnt"] or 0

            if cases_b > 0:
                increase_rate = (cases_a - cases_b) / cases_b
            else:
                increase_rate = 0.0

            # Compute rates
            mortality_rate = total_deaths / total_cases if total_cases > 0 else 0.0
            icu_rate = total_icu / total_cases if total_cases > 0 else 0.0
            # Proportion of hospitalized SRAG cases that had COVID vaccination.
            # This is NOT a population-level vaccination rate — it reflects the
            # vaccination status among inpatients only (VACINA_COV field).
            hospitalized_vaccination_rate = total_vaccinated / total_cases if total_cases > 0 else 0.0

            return {
                "success": True,
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "total_icu": total_icu,
                "total_vaccinated": total_vaccinated,
                "mortality_rate": round(mortality_rate, 4),
                "icu_rate": round(icu_rate, 4),
                "hospitalized_vaccination_rate": round(hospitalized_vaccination_rate, 4),
                "case_increase_rate": round(increase_rate, 4),
                "cases_last_30_days": cases_a,
                "cases_prev_30_days": cases_b
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Epidemiological metrics calculation failed: {str(e)}"
            }
