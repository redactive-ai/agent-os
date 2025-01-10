from enum import StrEnum

from pydantic import BaseModel

from redactive.agent_os.spec.agent import OAgentSpec


class EngagementState(BaseModel):
    """Internal Engagement State as defined in OpenAgentSpec, used for tool assertions"""
    user: dict = {}
    tools: dict = {}
    agents: dict = {}


class EngagementRuntimeData(BaseModel):
    """Runtime data for an engagement"""
    engagement_id: str
    oagent: OAgentSpec
    state: EngagementState
    internal: dict


class Engagement(BaseModel):
    """Engagement that is viewable by users and contains result once complete"""

    class Status(StrEnum): 
        AWAITING_LLM = "awaiting-llm"
        AWAITING_TOOL = "awaiting-tool"
        AWAITING_VERIFICATION = "awaiting-verification"
        COMPLETE = "complete"
    
    engagement_id: str
    oagent: OAgentSpec
    status: Status
    results: dict | None
    """MUST contain a text key"""
