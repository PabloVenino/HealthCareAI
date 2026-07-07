from typing import TypedDict, Dict, Any, List, Optional

class AgentState(TypedDict):
    query: str    
    filters: Dict[str, Any]
    validation_error: Optional[str]
    sql_query: Optional[str]
    sql_results: Optional[List[Dict[str, Any]]]
    metrics: Optional[Dict[str, Any]]
    charts: Optional[Dict[str, Any]]
    news: Optional[List[Dict[str, Any]]]
    report: Optional[str]
    execution_log: List[str]
