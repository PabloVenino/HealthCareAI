from typing import Dict, Any, List
from server.database.duckdb import get_db_client

class SQLTool:
    def __init__(self):
        self.db = get_db_client()

    def run_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Executes an SQL query against the DuckDB database and returns structured rows.
        Does NOT explain or summarize the results.
        """
        try:
            sql_upper = sql_query.upper()
            forbidden_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE TABLE"]
            for keyword in forbidden_keywords:
                if keyword in sql_upper:
                    return {
                        "success": False,
                        "error": f"Security Alert: Forbidden SQL keyword '{keyword}' detected."
                    }

            rows = self.db.execute_query(sql_query)
            return {
                "success": True,
                "rows": rows
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
