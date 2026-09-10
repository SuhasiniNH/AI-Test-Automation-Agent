from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from test_orchestration_graph import build_graph, TestRunState
import storage
import storage
import uuid 


app = FastAPI(title ="AI Test Automation Agent")
test_graph = build_graph()
storage.init_all()


class GenerateTestCase(BaseModel):
    requirement_text: str
    jira_issue_key : str

# API endpoints
@app.post("/generate-testcases")    
async def generate_testcases(requirement:GenerateTestCase):
    if not requirement.requirement_text and not requirement.jira_issue_key:
        raise HTTPException(status_code=400, detail="requirement not available")

    run_id = str(uuid.uuid4())
    requirement_text = requirement.requirement_text

    initial_state = TestRunState(run_id =run_id, requirement_text = requirement_text)
    final_state = test_graph.invoke(initial_state)

    storage.save_run(
        run_id,
        requirement_text,
        final_state["generated_cases"],
        final_state["execution_results"],
        final_state["analyzed_results"],
    )

    return {
        "run_id": run_id,
        "outcome": final_state["outcome"],
        "generated_cases": final_state["generated_cases"],
        "report": final_state["report"],
        "audit_log": final_state["audit_log"],
    }

@app.get("/results/{run_id}")
async def get_results(run_id: str):
    run = storage.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.get("/debug/{run_id}")
async def get_debug_info(run_id: str):
    """Returns failed test cases + suggestions for a run. Using run_id
    as the identifier here (rather than a separate error_id) since
    that's the one thing every stage of the pipeline already carries."""
    report = storage.get_report(run_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    failures = [d for d in report["details"] if d.get("status") == "failed"]
    return {"run_id": run_id, "failures": failures}


@app.get("/health")
async def health():
    return {"status": "ok"}    