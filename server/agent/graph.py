from langgraph.graph import StateGraph, START, END
from server.agent.state import AgentState
from server.agent.nodes import (
    validate_node,
    sql_node,
    metrics_node,
    charts_node,
    news_node,
    llm_report_node
)

def create_agent_graph():
    """
    Compiles the sequential node graph using LangGraph.
    Firstly defining nodes and then defining edges between them to create a workflow.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("validate", validate_node)
    workflow.add_node("sql_query", sql_node)
    workflow.add_node("compute_metrics", metrics_node)
    workflow.add_node("generate_charts", charts_node)
    workflow.add_node("search_news", news_node)
    workflow.add_node("generate_report", llm_report_node)

    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "sql_query")
    workflow.add_edge("sql_query", "compute_metrics")
    workflow.add_edge("compute_metrics", "generate_charts")
    workflow.add_edge("generate_charts", "search_news")
    workflow.add_edge("search_news", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()
