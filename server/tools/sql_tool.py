from typing import Dict, Any, List, Optional
import re
from server.database.duckdb import get_db_client

# Secondary defence layer: block explicit DML and known injection vectors.
# Primary defence is parameterised queries — this list is a belt-and-suspenders check.
_FORBIDDEN_KEYWORDS = frozenset([
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
    "TRUNCATE", "UNION",
])


class SQLTool:
    def __init__(self):
        self.db = get_db_client()

    def run_query(self, sql_query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Executes a parameterised SQL query against the DuckDB database and returns
        structured rows. Does NOT explain or summarise results.

        SECURITY:
          - Always pass user-supplied filter values through `params`, never via f-strings.
          - A secondary DML/UNION blocklist is applied to the query template itself as a
            belt-and-suspenders guard against accidental unsafe queries.
        """
        try:
            sql_upper = sql_query.upper()
            for keyword in _FORBIDDEN_KEYWORDS:
                # Match whole-word occurrences to avoid false positives (e.g. "column_update_ts")
                if re.search(rf"\b{keyword}\b", sql_upper):
                    return {
                        "success": False,
                        "error": f"Security Alert: Forbidden SQL keyword '{keyword}' detected."
                    }

            rows = self.db.execute_query(sql_query, params)
            return {
                "success": True,
                "rows": rows
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
