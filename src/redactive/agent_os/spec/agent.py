from typing import Literal

from pydantic import BaseModel, HttpUrl

from redactive.agent_os.spec.assertions import Assertion


class AgentCapabilityRestriction(BaseModel):
    class RequireReview(BaseModel):
        before: bool = False
        after: bool = False
        reviewer: Literal["user", "owner"]

    require_review: RequireReview | None = None
    input_assertion: Assertion
    output_assertion: Assertion


class AgentCapability(BaseModel):
    collect_results: bool = True
    collect_reasoning: bool = False
    user_identity: bool
    static_identity: str | None = None
    restrictions: AgentCapabilityRestriction | None = None

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
