"""ReportingAgent -- rolls results into a summary, files a ticket on failure,
and persists the report so /results and /debug have something to serve."""
# from utils.bug_ticket_service import file_ticket
import storage
from storage import save_report

def build_report(run_id: str, analyzed_results: list) -> dict:
    total = len(analyzed_results)
    failed = sum(1 for r in analyzed_results if r.get("status") == "failed")
    passed = total - failed
    outcome = "bug_detected" if failed else "passed"

    report = {
        "run_id": run_id,
        "total": total,
        "passed": passed,
        "failed": failed,
        "outcome": outcome,
        "details": analyzed_results,
    }

    # if outcome == "bug_detected":
    #     report["ticket_id"] = file_ticket(run_id, analyzed_results)

    save_report(run_id, report)
    return report
