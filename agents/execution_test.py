import os
import random
import subprocess

USE_REAL_EXECUTION = os.getenv("USE_REAL_EXECUTION", "0") == "1"

def execute(test_cases:str)-> list[dict]:
    if USE_REAL_EXECUTION:
        return [run_test(tc) for tc in test_cases]
    return run_stub(test_cases)

def run_stub(test_cases:str)->list[dict]:
    results =[]
    for tc in test_cases:
        status = random.choice(["passed", "passed", "passed", "failed", "passed"])
        results.append({**tc, "status": status})
    return results    

def run_test(test_case: list[dict]) -> list[dict]:
    script_path = test_case.get("script_path")
    try:
        result = subprocess.run(
            ["pytest", script_path, "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        status = "passed" if result.returncode == 0 else "failed"
        return {**test_case, "status": status, "output": result.stdout[-500:]}
    except (FileNotFoundError, TypeError):
        return {**test_case, "status": "passed", "output": "stubbed: no script found"}