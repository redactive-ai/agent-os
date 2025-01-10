
from typing import Protocol

from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData, EngagementUser
from redactive.agent_os.tools.protocol import Tool


class Runtime(Protocol):
    def __init__(self, all_tools: list[Tool]): ...

    def trigger_agent(self, oagent: OAgentSpec, user: EngagementUser, text: str | None) -> str: ...

    def get_engagement(self, engagement_id: str) -> Engagement: ...

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData: ...

    async def process_engagement(self, engagement_id: str) -> None: ...