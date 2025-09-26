# app.py
from fastapi import FastAPI, Query
from typing import List, Optional
from app.models import RemediationRequest, RemediationResponse
from app.orchestrator import run_pipeline

app = FastAPI(title="ABAP Remediation Service", version="1.0.0")

@app.post("/remediate", response_model=RemediationResponse)
async def remediate(payload: RemediationRequest, agents: Optional[List[str]] = Query(default=None)):
# agents: optional query param ?agents=legacy_abap,another_agent
 return await run_pipeline(payload, agent_ids=agents)