import os

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from server.database.duckdb import get_db_client

class ChartTool:
    def __init__(self):
        self.db = get_db_client()
        self.static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "charts"))
        os.makedirs(self.static_dir, exist_ok=True)

    def generate_charts(self, end_date: str, uf: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates daily cases (last 30 days) and monthly cases (last 12 months)
        up to end_date. Saves plots as PNGs and returns their filepaths/URLs.
        """
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # --- DAILY CASES CHART (Last 30 Days) ---
            start_daily_dt = end_dt - timedelta(days=30)
            start_daily = start_daily_dt.strftime("%Y-%m-%d")
            
            daily_query = """
                SELECT DT_NOTIFIC, COUNT(*) as case_count
                FROM srag
                WHERE DT_NOTIFIC BETWEEN ? AND ?
            """
            daily_params = [start_daily, end_date]
            if uf and uf.strip() and uf.upper() != "ALL":
                daily_query += " AND SG_UF_NOT = ?"
                daily_params.append(uf.upper().strip())
            daily_query += " GROUP BY DT_NOTIFIC ORDER BY DT_NOTIFIC"
            
            daily_data = self.db.execute_query(daily_query, tuple(daily_params))
            df_daily = pd.DataFrame(daily_data)
            
            all_dates = pd.date_range(start=start_daily_dt, end=end_dt).strftime("%Y-%m-%d")
            if df_daily.empty:
                df_daily = pd.DataFrame({"DT_NOTIFIC": all_dates, "case_count": 0})
            else:
                df_daily = df_daily.set_index("DT_NOTIFIC").reindex(all_dates, fill_value=0).reset_index()
                df_daily.columns = ["DT_NOTIFIC", "case_count"]

            # --- MONTHLY CASES CHART (Last 12 Months) ---
            start_monthly_dt = end_dt - timedelta(days=365)
            start_monthly = start_monthly_dt.strftime("%Y-%m-%d")
            
            monthly_query = """
                SELECT strftime('%Y-%m', DT_NOTIFIC) as month, COUNT(*) as case_count
                FROM srag
                WHERE DT_NOTIFIC BETWEEN ? AND ?
            """
            monthly_params = [start_monthly, end_date]
            if uf and uf.strip() and uf.upper() != "ALL":
                monthly_query += " AND SG_UF_NOT = ?"
                monthly_params.append(uf.upper().strip())
            monthly_query += " GROUP BY month ORDER BY month"
            
            monthly_data = self.db.execute_query(monthly_query, tuple(monthly_params))
            df_monthly = pd.DataFrame(monthly_data)
            
            # Fill missing months
            all_months = pd.date_range(start=start_monthly_dt, end=end_dt, freq='ME').strftime("%Y-%m").tolist()
            end_month_str = end_dt.strftime("%Y-%m")
            if end_month_str not in all_months:
                all_months.append(end_month_str)
                
            if df_monthly.empty:
                df_monthly = pd.DataFrame({"month": all_months, "case_count": 0})
            else:
                df_monthly = df_monthly.set_index("month").reindex(all_months, fill_value=0).reset_index()
                df_monthly.columns = ["month", "case_count"]

            return {
                "success": True,
                "daily_chart": df_daily.to_dict(orient="records"),
                "monthly_chart": df_monthly.to_dict(orient="records")
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Charts generation failed: {str(e)}"
            }
