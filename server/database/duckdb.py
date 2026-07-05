import os
import duckdb
from typing import Dict, Any, List

class DuckDBClient:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Create a local db file in the data folder
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "healthcare.db")
        else:
            self.db_path = db_path
        
        self.conn = duckdb.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Executes a query and returns the rows as a list of dictionaries.
        """
        try:
            if params:
                cursor = self.conn.execute(query, params)
            else:
                cursor = self.conn.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            raise RuntimeError(f"DuckDB query execution failed: {str(e)}")

    def close(self):
        self.conn.close()

# Shared singleton instance
_client = None

def get_db_client() -> DuckDBClient:
    global _client
    if _client is None:
        _client = DuckDBClient()
    return _client
