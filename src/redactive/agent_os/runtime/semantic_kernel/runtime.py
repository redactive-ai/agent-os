import logging
from datetime import UTC, datetime

from semantic_kernel.contents.chat_history import ChatHistory

from redactive.agent_os.runtime.assertions import run_cel_assertion
from redactive.agent_os.runtime.runtime_protocol import Runtime
from redactive.agent_os.runtime.semantic_kernel.agent_kernel import SemanticKernelAgentKernel
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData, EngagementState, EngagementUser
from redactive.agent_os.tools.protocol import Tool
from redactive.utils.random_gen import random_alpha_numeric_string

_logger = logging.getLogger(__name__)


class SemanticKernelRuntime(Runtime):
    _tools: list[Tool]
    _executions: dict[str, EngagementRuntimeData]

    def __init__(self, all_tools: list[Tool]):
        self._tools = all_tools
        self._executions = {}

    def create_engagement(self, oagent: OAgentSpec, user: EngagementUser) -> str:
        # TODO: ensure oagent spec is fulfillable by this runtime
        eng_id = random_alpha_numeric_string(8)
        history = ChatHistory()
        history.add_system_message(oagent.intent)
        execution_data = EngagementRuntimeData(
            engagement_id=eng_id,
            oagent=oagent,
            state=EngagementState(
                time_started=datetime.now(UTC),
                time_now=datetime.now(UTC),
                user=EngagementUser(
                    id=user.id,
                    email=user.email,
                ),
                recent={cap: None for cap in oagent.capabilities.keys()},
                history={cap: [] for cap in oagent.capabilities.keys()}
            ),
            internal=dict(history=history)
        )
        self._executions[eng_id] = execution_data
        return eng_id
    
    def append_to_engagement(self, engagement_id: str, text: str) -> None:
        engagement = self._executions[engagement_id]
        history: ChatHistory = engagement.internal["history"]
        history.add_user_message(text)
        engagement.capability_attempt_history.append("+external_input")

    @staticmethod
    def _parse_state(data: EngagementRuntimeData) -> Engagement.Status:
        if data.error:
            return Engagement.Status.ERROR
        
        history: ChatHistory = data.internal["history"]
        last_message = history.messages[-1]
        if last_message.finish_reason == "stop":
            return Engagement.Status.COMPLETE
        if last_message.finish_reason == "TOOL":
            return Engagement.Status.AWAITING_TOOL
        return Engagement.Status.AWAITING_LLM

    @staticmethod
    def _parse_results(data: EngagementRuntimeData) -> dict:
        results = {}
        chat_history: ChatHistory = data.internal["history"]
        for expose_key, expose_cel in data.oagent.exposes.items():
            result_value = run_cel_assertion(data.state, expose_cel)
            results[expose_key] = result_value
        results["text"] = chat_history.messages[-1].content
        return results

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData:
        return self._executions[engagement_id]

    def get_engagement(self, engagement_id: str) -> Engagement:
        runtime_data = self._executions[engagement_id]
        status = self._parse_state(runtime_data)

        return Engagement(
            engagement_id=engagement_id,
            oagent=runtime_data.oagent,
            user=runtime_data.state.user,
            status=status,
            results=self._parse_results(runtime_data) if status is Engagement.Status.COMPLETE else None
        )

    async def process_engagement(self, engagement_id: str) -> None:
        runtime_data = self._executions[engagement_id]
        
        if not runtime_data.error:
            try:
                if self._parse_state(runtime_data).is_ongoing():
                    # Possible improvement: cache agent kernels for re-use?
                    agent_kernel = SemanticKernelAgentKernel(agent_spec=runtime_data.oagent, tools=self._tools)
                    await agent_kernel.process(engagement_runtime_data=runtime_data)
            except Exception as exc:
                _logger.error("Engagement Error: %s", exc, exc_info=True)
                runtime_data.error = True