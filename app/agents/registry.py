from typing import Dict
from app.agents.base import Agent
from app.agents.replacement_agent.legacy_abap import LegacyABAPRemediationAgent
from app.agents.select_agent.select_abap import SelectABAPRemediationAgent
from app.agents.sort_agent.sort_abap import SortABAPRemediationAgent
from app.agents.table_agent.table_abap import TableABAPRemediationAgent


def get_agent_registry() -> Dict[str, Agent]:
    # Instantiate agents here. Add more agents as you build them.
    registry: Dict[str, Agent] = {
        "legacy_abap": LegacyABAPRemediationAgent(),
        "select_abap": SelectABAPRemediationAgent(),
        "sort_abap": SortABAPRemediationAgent(),
        "table_abap": TableABAPRemediationAgent(),
        # "another_agent": AnotherAgent(),
    }
    return registry