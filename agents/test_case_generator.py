import os
import json
from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()
api_key= os.getenv("OPENAI_API_KEY")

client =  OpenAI(api_key=api_key)

PROMPT_TEMPLATE = """You are a QA engineer. Given the requirement below,
    write 3-5 test cases covering the happy path, edge cases, and failure modes.

    Requirement:
    {requirement_text}

    Respond with ONLY valid JSON, no other text, in exactly this shape:
    {{"test_cases": [{{"id": "TC-1", "description": "..."}}]}}
    """

USE_LLM  = os.getenv("USE_LLM", "0") =="1"

def generate_test(requirement_text:str) -> list[dict]:
    if USE_LLM :
        return generate_test_from_llm(requirement_text)
    return generate_stub(requirement_text)


def generate_stub(requirement_text:str) -> list[dict]:
    return [
        {"id": "TC-1", "description": f"Happy path: {requirement_text[:40]}"},
        {"id": "TC-2", "description": "Edge case: link expires exactly at 30 minutes"},
        {"id": "TC-3", "description": "Failure case: link used twice"},
    ]


def generate_test_from_llm(requirement_text:str) -> list[dict]:
    response = client.responses.create(
        model = "gpt-5.4",
        input=[
            {"role": "user", "content": PROMPT_TEMPLATE.format(requirement_text=requirement_text)}
        ],
        max_output_tokens =1000
    )
    raw_text = response.output_text.strip()
    result = json.loads(raw_text)
    return result["test_cases"]