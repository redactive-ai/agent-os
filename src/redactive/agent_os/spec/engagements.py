from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from redactive.agent_os.spec.agent import OAgentSpec


class EngagementUser(BaseModel):
    id: str
    email: str

class EngagementState(BaseModel):
    """Internal Engagement State as defined in OpenAgentSpec, used for tool assertions"""
    class CapabilityUse(BaseModel):
        inputs: dict
        outputs: dict | None

    started_at: datetime
    user: EngagementUser

    recent_name: str = ""
    recent: dict[str, CapabilityUse | None]
    history_names: list[str] = Field(default_factory=lambda: [])
    history: dict[str, list[CapabilityUse]]


class EngagementRuntimeData(BaseModel):
    """Runtime data for an engagement"""
    engagement_id: str
    oagent: OAgentSpec
    state: EngagementState
    error: bool = False
    internal: dict


class Engagement(BaseModel):
    """Engagement that is viewable by users and contains result once complete"""

    class Status(StrEnum): 
        AWAITING_LLM = "awaiting-llm"
        AWAITING_TOOL = "awaiting-tool"
        AWAITING_VERIFICATION = "awaiting-verification"
        AWAITING_ADDITIONAL_INPUT = "awaiting-additional-input"
        COMPLETE = "complete"
        ERROR = "error"

        def is_ongoing(self) -> bool:
            return self != Engagement.Status.COMPLETE and self != Engagement.Status.ERROR
    
    engagement_id: str
    oagent: OAgentSpec
    user: EngagementUser
    status: Status
    results: dict | None
    """MUST contain a text key"""
