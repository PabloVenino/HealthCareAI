from fastapi import APIRouter, HTTPException
from server.models.report import ReportRequest, ReportResponse
from server.agent.orchestrator import AgentOrchestrator
from server.services.data_loader import DataLoader

router = APIRouter(prefix="/api")

@router.post("/report", response_model=ReportResponse)
def generate_epidemiological_report(request: ReportRequest):
    """
    Triggers the LangGraph agent execution pipeline to create an audit-compliant
    epidemiological report with charts, metrics, and news.
    """
    # Ensure data is clean and registered as a DuckDB view before querying
    loader = DataLoader()
    loader.ensure_data_ready()
    
    # Run LangGraph Orchestrator
    orchestrator = AgentOrchestrator()
    result_state = orchestrator.run_agent(request.query, request.filters)
    
    if result_state.get("validation_error"):
        raise HTTPException(status_code=400, detail=result_state["validation_error"])
        
    # Map LangGraph final state to structured API response
    response = ReportResponse(
        metrics=result_state.get("metrics"),
        charts=result_state.get("charts"),
        explanation=result_state.get("report") or "No report content generated.",
        news=result_state.get("news") or [],
        execution_log=result_state.get("execution_log") or []
    )
    return response
