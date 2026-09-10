"""FailureAnalysisAgent -- attaches a suggestion to every failed test case."""
# from utils.log_parser import extract_error_signal


def extract_error_signal(output: str) -> str:
    # Temporary stub until you implement real parsing
    if "timeout" in output.lower():
        return "Investigate timeout issues"
    if "connection" in output.lower():
        return "Check network connectivity"
    return None

def analyze(execution_results: list) -> list:
    analyzed = []
    for result in execution_results:
        entry = dict(result)
        if entry.get("status") == "failed":
            signal = extract_error_signal(entry.get("output", ""))
            entry["suggestion"] = signal or "Check for a possible race condition or stale test data."
        analyzed.append(entry)
    return analyzed
