import os
import json
from datetime import date
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from app.models import RemediationRequest, RemediationResponse
from app.agents.select_agent.select_pattern_loader import load_rag_patterns
from app.agents.select_agent.select_utils import scan_code_for_patterns, add_pwc_tag

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1")
# RAG_FILE = os.getenv("RAG_FILE", "rag_patterns.json") 
# Get the directory where this script lives (e.g., app/)
ROOT = os.path.dirname(os.path.abspath(__file__))
RAG_FILE = os.getenv(
    "RAG_FILE",
    os.path.join(ROOT, "select_patterns.json")
)

_PATTERNS_CACHE: Optional[List[Dict[str, Any]]] = None


def _get_patterns() -> List[Dict[str, Any]]:
    global _PATTERNS_CACHE
    if _PATTERNS_CACHE is None:
        _PATTERNS_CACHE = load_rag_patterns(RAG_FILE)
    return _PATTERNS_CACHE


def _create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.2
        # tracing via env: LANGCHAIN_TRACING_V2=true, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
    )


SYSTEM_PROMPT = """You are an expert ABAP developer and remediation assistant.
You will be given:

original ABAP code
a list of findings with exact patterns (legacy usage) and suggested replacements.
Your task:

Update the code by applying the specified replacements precisely.
Never Add Order By where FOR ALL ENTRIES is present in Select query.(Mandatory).
Do not change unrelated parts of the code.
Use valid ABAP syntax.
For each change you make, add an ABAP comment tag on the changed line or just above it: "Added By Pwc {tag_date}
"""

HUMAN_PROMPT = """Context:
pgm_name={pgm_name}
inc_name={inc_name}
type={type}
name={name}
class_implementation={class_implementation}

Original ABAP code:
{code}

Findings (JSON):
{findings_json}

Instructions:

Apply all replacements described in the findings list.
Maintain code formatting where possible.
Always include the ABAP comment tag "* Added By Pwc {tag_date}" after each change.
Output only the final ABAP code. 
No keyword like abap or abap code only the final code. nothting extra Nothing less(Mandatory)
Never explicitly end and block of code like(ENDFORM , ENDMETHOD) unless present in Original Code. (Mandatory) 
"""


class SelectABAPRemediationAgent:
    id = "select_abap"
    description = "Scans ABAP code for legacy transaction/pattern usage using RAG JSON and remediates via GPT-4.1."

    async def run(self, payload: RemediationRequest) -> RemediationResponse:
        original_code = payload.code or ""
        patterns = _get_patterns()        
        findings = scan_code_for_patterns(original_code, patterns)        
        

        # If no findings, return code with PwC tag; do not call LLM
        if not findings:
            remediated = original_code
            return RemediationResponse(
                pgm_name=payload.pgm_name,
                inc_name=payload.inc_name,
                type=payload.type,
                name=payload.name or "",
                class_implementation=payload.class_implementation or "",
                original_code=original_code,
                remediated_code=remediated
            )

        # If findings exist, call GPT-4.1 via LangChain        
        remediated_code = await self._remediate_code_via_llm(original_code, findings, payload)

        # # Safety: ensure PwC tag exists even if model missed it
        # remediated_code = add_pwc_tag(remediated_code)

        return RemediationResponse(
            pgm_name=payload.pgm_name,
            inc_name=payload.inc_name,
            type=payload.type,
            name=payload.name or "",
            class_implementation=payload.class_implementation or "",
            original_code=original_code,
            remediated_code=remediated_code
        )

    async def _remediate_code_via_llm(
        self, 
        original_code: str, 
        findings: List[Dict[str, Any]],
        payload: RemediationRequest
    ) -> str:
        tag_date = date.today().strftime("%Y-%m-%d")
        llm = _create_llm()

        system_msg = SystemMessage(content=SYSTEM_PROMPT.format(tag_date=tag_date))
        human_msg = HumanMessage(
            content=HUMAN_PROMPT.format(
                pgm_name=payload.pgm_name,
                inc_name=payload.inc_name,
                type=payload.type,
                name=payload.name or "",
                class_implementation=payload.class_implementation or "",
                code=original_code,
                findings_json=json.dumps(findings, indent=2),
                tag_date=tag_date
            )
        )

        result = await llm.ainvoke([system_msg, human_msg])
        return result.content.strip()