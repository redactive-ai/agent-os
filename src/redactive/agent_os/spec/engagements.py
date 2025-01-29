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
        inputs_allowed: bool
        success: bool
        outputs_allowed: bool
        outputs: dict

    time_started: datetime
    time_now: datetime
    
    user: EngagementUser

    inputs: dict = Field(default_factory=lambda: {})
    """The current input to the tool"""
    outputs: dict = Field(default_factory=lambda: {})
    """The current tool output"""

    recent_name: str = ""
    """The most recent tool name, prior to this one"""

    recent: dict[str, CapabilityUse | None]
    """The inputs and outputs of each of the most recent usages of each tool"""

    history_names: list[str] = Field(default_factory=lambda: [])
    """An ordered list of names of each tool invocation"""

    history: dict[str, list[CapabilityUse]]
    """Ordered list of inputs and outputs for each tool"""


class EngagementRuntimeData(BaseModel):
    """Runtime data for an engagement"""
    engagement_id: str
    oagent: OAgentSpec
    state: EngagementState

    capability_attempt_history: list[str] = []
    """Ordered list of every capability invocation this engagement has attempted. Use to detect short circuiting"""

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
