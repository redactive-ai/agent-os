import logging
from datetime import datetime

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.contents.utils.finish_reason import FinishReason
from semantic_kernel.utils.logging import setup_logging

from redactive.agent_os.agent_runtimes.semantic_kernel.native_tool_to_function import (
    convert_native_tool_to_kernel_function,
)
from redactive.agent_os.runtime_protocols import ToolRuntime
from redactive.agent_os.secrets import get_secret
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import EngagementRuntimeData
from redactive.agent_os.tool_runtimes.engagement_enforcer import EngagementEnforcer

_logger = logging.getLogger(__name__)

# Set the logging level for  semantic_kernel.kernel to DEBUG.
setup_logging()
logging.getLogger("kernel").setLevel(logging.DEBUG)

class SemanticKernelAgentKernel:
    _agent_spec: OAgentSpec
    _tool_runtime: ToolRuntime
    _engagement_enforcer: EngagementEnforcer
    _kernel: Kernel
    _llm: OpenAIChatCompletion
    _llm_settings: PromptExecutionSettings

    def __init__(self, agent_spec: OAgentSpec, tool_runtime: ToolRuntime):
        self._agent_spec = agent_spec
        self._engagement_enforcer = EngagementEnforcer()
        self._kernel = Kernel()
        self._llm = OpenAIChatCompletion(
            service_id="chat",
            ai_model_id="gpt-4o",
            api_key=get_secret("openai__api-key"),
        )
        self._kernel.add_service(self._llm)

        for tool_name, capability in self._agent_spec.capabilities.items():
            tool = tool_runtime.get_tool_by_name(tool_name=tool_name)
            self._kernel.add_function(
                plugin_name=tool.name,
                function=convert_native_tool_to_kernel_function(tool=tool, capability=capability),
            )

        # TODO: understand settings:
        self._llm_settings = self._kernel.get_prompt_execution_settings_from_service_id("chat")
        self._llm_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=False)
        
    async def process(self, engagement_runtime_data: EngagementRuntimeData):
        history: ChatHistory = engagement_runtime_data.internal["history"]

        if len(history) > 0:
            previous_finish_reason = history.messages[-1].finish_reason
            if (previous_finish_reason == FinishReason.STOP):
                return

            if (previous_finish_reason == FinishReason.TOOL_CALLS):
                await self._use_tool(engagement_runtime_data=engagement_runtime_data)
                return
                
        # Otherwise always LLM CALL (TODO: confirm this?)
        await self._call_llm(engagement_runtime_data=engagement_runtime_data)

    async def _use_tool(self, engagement_runtime_data: EngagementRuntimeData):
        history: ChatHistory = engagement_runtime_data.internal["history"]
        print(f"AGENT USING {len(history.messages[-1].items)} TOOLS")

        for function_call_content in history.messages[-1].items:
            print(function_call_content)
            assert isinstance(function_call_content, FunctionCallContent)

            if self._engagement_enforcer.check_short_circuit(engagement=engagement_runtime_data):
                engagement_runtime_data.internal["error"] = "agent short circuited"
                return

            kernel_function = self._kernel.get_function(function_call_content.plugin_name, function_call_content.function_name)
            kernel_args = function_call_content.to_kernel_arguments()

            allowed, error_response = self._engagement_enforcer.check_input_restrictions(
                engagement=engagement_runtime_data,
                tool_name=kernel_function.name,
                inputs=kernel_args
            )
            if not allowed:
                function_result_content = FunctionResultContent.from_function_call_content_and_result(
                    function_call_content, error_response
                )
                history.add_message(function_result_content.to_chat_message_content())
                return
            
            results = await self._tool_runtime.invoke_tool(tool_name=kernel_function.name, inputs=kernel_args)

            allowed, error_response = self._engagement_enforcer.check_output_restrictions(
                engagement=engagement_runtime_data,
                tool_name=kernel_function.name,
                outputs=results
            )
            if not allowed:
                function_result_content = FunctionResultContent.from_function_call_content_and_result(
                    function_call_content, error_response
                )
                history.add_message(function_result_content.to_chat_message_content())
                return

            function_result_content = FunctionResultContent.from_function_call_content_and_result(
                function_call_content, results
            )
            history.add_message(function_result_content.to_chat_message_content())

    async def _call_llm(self, engagement_runtime_data: EngagementRuntimeData):
        history: ChatHistory = engagement_runtime_data.internal["history"]
        _logger.info(f"Calling LLM {datetime.now().second}")
        result = await self._llm.get_chat_message_content(
            chat_history=history,
            settings=self._llm_settings,
            kernel=self._kernel,
        )
        _logger.info(f"LLM returned response {datetime.now().second}")
        if result is not None:
            history.add_message(result)

