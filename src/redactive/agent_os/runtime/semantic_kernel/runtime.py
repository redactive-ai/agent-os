from semantic_kernel.contents.chat_history import ChatHistory

from redactive.agent_os.runtime.runtime_protocol import Runtime
from redactive.agent_os.runtime.semantic_kernel.agent_kernel import SemanticKernelAgentKernel
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData, EngagementState
from redactive.agent_os.tools.protocol import Tool
from redactive.utils.random_gen import random_alpha_numeric_string


class SemanticKernelRuntime(Runtime):
    _tools: list[Tool]
    _executions: dict[str, EngagementRuntimeData]

    def __init__(self, all_tools: list[Tool]):
        self._tools = all_tools
        self._executions = {}

    def trigger_agent(self, oagent: OAgentSpec, text: str | None) -> str:
        # TODO: ensure oagent spec is fulfillable by this runtime
        eng_id = random_alpha_numeric_string(8)
        execution_data = EngagementRuntimeData(
            engagement_id=eng_id,
            oagent=oagent,
            state=EngagementState(),
            internal=dict(history=ChatHistory())
        )
        self._executions[eng_id] = execution_data
        
        if text is not None:
            history: ChatHistory = execution_data.internal["history"]
            history.add_user_message(text)
        
        return eng_id

    @staticmethod
    def _parse_state(history: ChatHistory) -> Engagement.Status:
        last_message = history.messages[-1]
        if last_message.finish_reason == "stop":
            return Engagement.Status.COMPLETE
        if last_message.finish_reason == "TOOL":
            return Engagement.Status.AWAITING_TOOL
        return Engagement.Status.AWAITING_LLM

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData:
        return self._executions[engagement_id]


    def get_engagement_state(self, engagement_id: str) -> EngagementState:
        runtime_data = self.get_engagement_runtime_data(engagement_id=engagement_id)
        return runtime_data.state


    def get_engagement(self, engagement_id: str) -> Engagement:
        runtime_data = self._executions[engagement_id]
        chat_history: ChatHistory = runtime_data.internal["history"]
        status = self._parse_state(chat_history)
        results = None

        if status == Engagement.Status.COMPLETE:
            results = {
                # TODO: add other EXPOSES from oagent spec
                "text": chat_history.messages[-1].content
            }

        return Engagement(
            engagement_id=engagement_id,
            oagent=runtime_data.oagent,
            status=self._parse_state(chat_history),
            results=results
        )


    async def process_engagement(self, engagement_id: str) -> None:
        runtime_data = self._executions[engagement_id]
        chat_history: ChatHistory = runtime_data.internal["history"]

        if self._parse_state(chat_history) == Engagement.Status.COMPLETE:
            return        
        
        # Possible improvement: cache agent kernels for re-use
        agent_kernel = SemanticKernelAgentKernel(agent_spec=runtime_data.oagent, tools=self._tools)

        await agent_kernel.process(engagement_runtime_data=runtime_data)
