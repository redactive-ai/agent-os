
from typing import Protocol

from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.synapse import SynapseExecutionState, SynapseStatus
from redactive.agent_os.tools.protocol import Tool


class Runtime(Protocol):
    def __init__(self, all_tools: list[Tool]): ...

    def trigger_agent(self, oagent: OAgentSpec, text: str | None) -> str: ...

    def get_synapse_status(self, syn_id: str) -> SynapseStatus: ...

    def get_synapse_execution_state(self, syn_id: str) -> SynapseExecutionState: ...

    async def process_synapse(self, syn_id: str) -> None: ...