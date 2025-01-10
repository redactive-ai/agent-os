from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AgentCapabilityRestriction(BaseModel):

    require_review: Literal["user", "owner"] | None = None
    assert_: str | None = Field(default=None, alias="assert")


class AgentCapability(BaseModel):
    collect_results: bool = True
    collect_reasoning: bool = False
    user_identity: bool
    static_identity: str | None = None
    input_restriction: AgentCapabilityRestriction | None = None
    output_restriction: AgentCapabilityRestriction | None = None

class AgentProofreading(BaseModel):
    tool: HttpUrl
    filter_: str | None
    transform: str | None

class AgentLifespan(BaseModel):
    memory: bool
    short_circuit: int

class OAgentSpec(BaseModel):
    kind: Literal["openOAgentSpec:v1/agent"] = "openOAgentSpec:v1/agent"
    uri: HttpUrl
    description: str
    intent: str
    owner: str
    capabilities: dict[str, AgentCapability]
    proofreading: AgentProofreading | None = None
    lifespan: AgentLifespan | None = None
