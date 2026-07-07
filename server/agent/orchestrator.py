from typing import Dict, Any, Optional
from server.agent.graph import create_agent_graph

class AgentOrchestrator:
    def __init__(self):
        self.graph = create_agent_graph()


    def run_agent(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the LangGraph agent chain with initial state parameters.
        """
        initial_state = {
            "query": query,
            "filters": filters or {},
            "validation_error": None,
            "sql_query": None,
            "sql_results": [],
            "metrics": None,
            "charts": None,
            "news": [],
            "report": None,
            "execution_log": []
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state
