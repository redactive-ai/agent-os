from pydantic import BaseModel

from redactive.agent_os.runtime.execution_status import ExecutionStatus
from redactive.agent_os.spec.agent import OAgentSpec


class Synapse(BaseModel):
    user: dict = {}
    tools: dict = {}
    agents: dict = {}


class SynapseExecutionState(BaseModel):
    syn_id: str
    oagent: OAgentSpec
    synapse: Synapse
    runtime_data: dict

class SynapseStatus(BaseModel):
    oagent: OAgentSpec
    status: ExecutionStatus
    results: dict | None
    """MUST contain a text key"""