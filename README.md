AI Test Automation Agent:

An agentic AI pipeline that turns a plain-language requirement into test cases, executes them, triages failures, and produces a report — exposed as a REST API built with FastAPI and orchestrated with LangGraph.

Overview:
Given a requirement (and an optional Jira issue key), the agent automatically:
Generates test cases covering the happy path, edge cases, and failure modes.
Executes those test cases.
Analyzes any failures and attaches a suggested root cause.
Builds a pass/fail report and persists it for later retrieval.
Each stage is a node in a LangGraph state graph, with a single Pydantic model carrying state between them and an audit trail recorded at every step.

Architecture:
``` text
Client
  |  POST /generate-testcases
  v
Generate tests        (LLM via OpenAI, or deterministic stub)
  |
  v
Execute tests          (pytest subprocess, or randomized stub)
  |
  v
Analyze failures       (keyword-based root-cause suggestion)
  |
  v
Build report           (pass/fail totals, outcome, persisted)
  |
  v
Return result to client

The graph is built and compiled in test_orchestration_graph.py using LangGraph's StateGraph. The shared state object, TestRunState, is a Pydantic model holding:
```
Field	Description
run_id	Unique identifier for the run (UUID)
requirement_text	The input requirement
generated_cases	Test cases produced by the generator
execution_results	Pass/fail results per test case
analyzed_results	Execution results annotated with failure suggestions
report	Final aggregated report
outcome	"passed" or "bug_detected"
audit_log	Human-readable trail of what happened at each node
Tech stack
LangGraph — orchestrates the multi-node pipeline via StateGraph
OpenAI API — powers LLM-based test case generation
FastAPI + Uvicorn — REST API layer
Pydantic — schema and state validation (TestRunState, request models)
SQLAlchemy (via a storage module) — persistence for runs and reports
pytest — real test execution when enabled
