from typing import Literal

from pydantic import BaseModel, Field


class CapabilityRestriction(BaseModel):
    class Config:
        extra = 'forbid'

    require_review: Literal["user", "owner"] | None = None
    assertion: str | None = None


class Capability(BaseModel):
    class Config:
        extra = 'forbid'

    collect_results: bool = True
    user_identity: bool = True
    static_identity: str | None = None
    input_restriction: CapabilityRestriction | None = None
    output_restriction: CapabilityRestriction | None = None

class Guardrail(BaseModel):
    class Config:
        extra = 'forbid'

    tool_name: str
    assertion: str | None = None

class Guardrails(BaseModel):
    class Config:
        extra = 'forbid'

    input: Guardrail | None = None
    output: Guardrail | None = None

class Lifespan(BaseModel):
    class Config:
        extra = 'forbid'

    retain_memory: bool | None = None
    short_circuit: int | None = None

class OAgentSpec(BaseModel):
    class Config:
        extra = 'forbid'

    kind: Literal["openOAgentSpec:v1/agent"] = "openOAgentSpec:v1/agent"
    name: str
    description: str
    intent: str
    owner: str

    capabilities: dict[str, Capability] = Field(default_factory=lambda: {})
    
    guardrails: Guardrails | None = None
    
    exposes: dict[str, str] = Field(default_factory=lambda: {})

    lifespan: Lifespan | None = None