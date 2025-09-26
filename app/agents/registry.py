from typing import Dict
from app.agents.base import Agent
from app.agents.replacement_agent.legacy_abap import LegacyABAPRemediationAgent
from app.agents.select_agent.select_abap import SelectABAPRemediationAgent


def get_agent_registry() -> Dict[str, Agent]:
    # Instantiate agents here. Add more agents as you build them.
    registry: Dict[str, Agent] = {
        "legacy_abap": LegacyABAPRemediationAgent(),
        "select_abap": SelectABAPRemediationAgent(),
        # "another_agent": AnotherAgent(),
    }
    return registry