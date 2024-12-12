from semantic_kernel.contents.chat_history import ChatHistory

from redactive.agent_os.runtime.execution_status import ExecutionStatus
from redactive.agent_os.runtime.runtime_protocol import Runtime
from redactive.agent_os.runtime.semantic_kernel.agent_kernel import SemanticKernelAgentKernel
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.synapse import Synapse, SynapseExecutionState, SynapseStatus
from redactive.agent_os.tools.protocol import Tool
from redactive.utils.random_gen import random_alpha_numeric_string


class SemanticKernelRuntime(Runtime):
    _tools: list[Tool]
    _executions: dict[str, SynapseExecutionState]

    def __init__(self, all_tools: list[Tool]):
        self._tools = all_tools
        self._executions = {}

    def trigger_agent(self, oagent: OAgentSpec, text: str | None) -> str:
        # TODO: ensure oagent spec is fulfillable by this runtime
        syn_id = random_alpha_numeric_string(8)
        execution_data = SynapseExecutionState(
            syn_id=syn_id,
            oagent=oagent,
            synapse=Synapse(),
            runtime_data=dict(history=ChatHistory())
        )
        self._executions[syn_id] = execution_data
        
        if text is not None:
            history: ChatHistory = execution_data.runtime_data["history"]
            history.add_user_message(text)
        
        return syn_id

    @staticmethod
    def _parse_state(history: ChatHistory) -> ExecutionStatus:
        last_message = history.messages[-1]
        if last_message.finish_reason == "stop":
            return ExecutionStatus.COMPLETE
        if last_message.finish_reason == "TOOL":
            return ExecutionStatus.AWAITING_TOOL
        return ExecutionStatus.AWAITING_LLM

    def get_synapse(self, syn_id: str) -> Synapse:
        execution_data = self.get_synapse_execution_state(syn_id=syn_id)
        return execution_data.synapse


    def get_synapse_status(self, syn_id: str) -> SynapseStatus:
        execution_state = self._executions[syn_id]
        chat_history: ChatHistory = execution_state.runtime_data["history"]
        status = self._parse_state(chat_history)
        results = None

        if status == ExecutionStatus.COMPLETE:
            results = {
                # TODO: add other EXPOSES from oagent spec
                "text": chat_history.messages[-1].content
            }

        return SynapseStatus(
            oagent=execution_state.oagent,
            status=self._parse_state(chat_history),
            results=results
        )

    def get_synapse_execution_state(self, syn_id: str) -> SynapseExecutionState:
        return self._executions[syn_id]

    async def process_synapse(self, syn_id: str) -> None:
        execution_state = self._executions[syn_id]
        chat_history: ChatHistory = execution_state.runtime_data["history"]

        if self._parse_state(chat_history) == ExecutionStatus.COMPLETE:
            return        
        
        # Possible improvement: cache agent kernels for re-use
        agent_kernel = SemanticKernelAgentKernel(agent_spec=execution_state.oagent, tools=self._tools)

        await agent_kernel.process(execution_state=execution_state)
