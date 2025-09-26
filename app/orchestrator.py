import os
from typing import List, Optional
from app.models import RemediationRequest, RemediationResponse
from app.agents.registry import get_agent_registry
# from replacement_agent.utils import add_pwc_tag

# Default pipeline can be set via env, e.g. "legacy_abap,formatter"
DEFAULT_PIPELINE = [
    a.strip() for a in os.getenv("AGENT_PIPELINE", "legacy_abap, select_abap").split(",") if a.strip()
]


async def run_pipeline(payload: RemediationRequest, agent_ids: Optional[List[str]] = None) -> RemediationResponse:
    """
    Sequentially runs the specified agents. Each agent consumes RemediationRequest
    and returns RemediationResponse. The remediated_code becomes the code for
    the next agent. Final response retains the initial original_code.
    """
    registry = get_agent_registry()
    pipeline = agent_ids if agent_ids else DEFAULT_PIPELINE    
    # Initial conditions
    initial_original_code = payload.code or ""
    current_request = payload

    last_response: Optional[RemediationResponse] = None

    for agent_id in pipeline:
        agent = registry.get(agent_id)        
        if not agent:
            # Skip unknown agents silently or raise error if preferred
            continue
        last_response = await agent.run(current_request)

        # Prepare next request using previous remediated code
        current_request = RemediationRequest(
            pgm_name=payload.pgm_name,
            inc_name=payload.inc_name,
            type=payload.type,
            name=payload.name or "",
            class_implementation=payload.class_implementation or "",
            code=last_response.remediated_code
        )

    # If no agent ran, pass through with PwC tag
    # if last_response is None:
    #     return RemediationResponse(
    #         pgm_name=payload.pgm_name,
    #         inc_name=payload.inc_name,
    #         type=payload.type,
    #         name=payload.name or "",
    #         class_implementation=payload.class_implementation or "",
    #         original_code=initial_original_code,
    #         remediated_code=add_pwc_tag(initial_original_code)
        # )

    # Ensure original_code is the initial code for the final response
    final_resp = RemediationResponse(
        pgm_name=payload.pgm_name,
        inc_name=payload.inc_name,
        type=payload.type,
        name=payload.name or "",
        class_implementation=payload.class_implementation or "",
        original_code=initial_original_code,
        remediated_code=last_response.remediated_code
    )

    # Safety: ensure PwC tag present
    # final_resp.remediated_code = add_pwc_tag(final_resp.remediated_code)
    return final_resp