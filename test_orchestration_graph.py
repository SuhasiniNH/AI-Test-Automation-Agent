from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from agents import test_case_generator
from agents import execution_test
from agents import failure_analysis_agent
from agents import reporting_agent
from typing import Literal

class TestRunState(BaseModel):
    run_id:str
    requirement_text: str

    generated_cases: list[dict] = []
    execution_results: list[dict] = []
    analyzed_results: list[dict] = []
    report: dict = {}

    outcome: Literal["passed", "bug_detected"] = None
    audit_log: list[str] = []

def generate_test_node(state: TestRunState)-> TestRunState:
    state.generated_cases = test_case_generator.generate_test(state.requirement_text)
    state.audit_log.append(f"Generated {len(state.generated_cases)} test cases")
    return state

def execute_tests_node(state: TestRunState) -> TestRunState:
    state.execution_results = execution_test.execute(state.generated_cases)
    state.audit_log.append("Executed test cases")
    return state


def analyze_failures_node(state: TestRunState) -> TestRunState:
    state.analyzed_results = failure_analysis_agent.analyze(state.execution_results)
    state.audit_log.append("Analyzed failures")
    return state


def reporting_node(state: TestRunState) -> TestRunState:
    state.report = reporting_agent.build_report(state.run_id, state.analyzed_results)
    state.outcome = state.report["outcome"]
    state.audit_log.append(f"Report: {state.report}")
    return state

def route_by_outcome(state: TestRunState) -> str:
    return state.outcome


def build_graph():
    graph = StateGraph(TestRunState)

    graph.add_node("generate_tests", generate_test_node)
    graph.add_node("execute_tests", execute_tests_node)
    graph.add_node("analyze_failures", analyze_failures_node)
    graph.add_node("report", reporting_node)

    graph.set_entry_point("generate_tests")
    graph.add_edge("generate_tests", "execute_tests")
    graph.add_edge("execute_tests", "analyze_failures")
    graph.add_edge("analyze_failures", "report")

    graph.add_conditional_edges(
        "report",
        route_by_outcome,
        {"passed": END, "bug_detected": END},
    )

    return graph.compile()



