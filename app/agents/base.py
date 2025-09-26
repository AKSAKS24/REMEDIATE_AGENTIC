from typing import Protocol
from app.models import RemediationRequest, RemediationResponse


class Agent(Protocol):
    id: str
    description: str

    async def run(self, payload: RemediationRequest) -> RemediationResponse:
        ...