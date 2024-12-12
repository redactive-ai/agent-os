
import logging
from datetime import datetime

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.contents.utils.finish_reason import FinishReason
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent

from redactive.agent_os.runtime.errors import RestrictedToolInput, RestrictedToolOutput
from redactive.agent_os.runtime.tool_sandbox import ToolSandbox
from redactive.agent_os.secrets import get_secret
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.synapse import SynapseExecutionState
from redactive.agent_os.tools.protocol import Tool

_logger = logging.getLogger(__name__)

# Set the logging level for  semantic_kernel.kernel to DEBUG.
setup_logging()
logging.getLogger("kernel").setLevel(logging.DEBUG)

class SemanticKernelAgentKernel:
    _agent_spec: OAgentSpec    
    _kernel: Kernel
    _llm: OpenAIChatCompletion
    _llm_settings: PromptExecutionSettings

    def __init__(self, agent_spec: OAgentSpec, tools: list[Tool]):
        self._agent_spec = agent_spec
        self._kernel = Kernel()
        self._llm = OpenAIChatCompletion(
            service_id="chat",
            ai_model_id="gpt-4-turbo",
            api_key=get_secret("openai__api-key"),
        )
        self._kernel.add_service(self._llm)

        for tool_name, capability in self._agent_spec.capabilities.items():
            matching_tools = [t for t in tools if t.name == tool_name]
            if len(matching_tools) < 0:
                raise NotImplementedError(f"Agent OS does not know about tool '{tool_name}'")
            
            tool = matching_tools[0]
            kernel_func = kernel_function(func=tool, name=tool.name, description=tool.description)
            self._kernel.add_function(plugin_name=tool.name, function=kernel_func)

        # TODO: understand settings:
        self._llm_settings = self._kernel.get_prompt_execution_settings_from_service_id("chat")
        self._llm_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=False)
        
    async def process(self, execution_state: SynapseExecutionState):
        history: ChatHistory = execution_state.runtime_data["history"]
        previous_finish_reason = history.messages[-1].finish_reason

        if (previous_finish_reason == FinishReason.STOP):
            return

        if (previous_finish_reason == FinishReason.TOOL_CALLS):
            await self._use_tool(execution_state=execution_state)
            return
                
        else: # Otherwise always LLM CALL (TODO: confirm this?)
            await self._call_llm(execution_state=execution_state)

    async def _use_tool(self, execution_state: SynapseExecutionState):
        history: ChatHistory = execution_state.runtime_data["history"]
        function_call_content = history.messages[-1].items[0]
        assert isinstance(function_call_content, FunctionCallContent)
        print("CALL TOOL BEGIN")

        kernel_function = self._kernel.get_function(function_call_content.plugin_name, function_call_content.function_name)
        tool_name = kernel_function.name
        agent_capability = execution_state.oagent.capabilities[tool_name]
        
        kernel_args = function_call_content.to_kernel_arguments()
        execution_state.synapse.tools[tool_name] = { "inputs": kernel_args }

        if not ToolSandbox.assert_synapse(agent_capability.input_restriction, execution_state.synapse):
            raise RestrictedToolInput()
        
        function_result = await kernel_function(self._kernel, kernel_args)
        function_result_content = FunctionResultContent.from_function_call_content_and_result(
            function_call_content, function_result
        )
        execution_state.synapse.tools["outputs"] = function_result_content.result

        if not ToolSandbox.assert_synapse(agent_capability.output_restriction, execution_state.synapse):
            raise RestrictedToolOutput()

        history.add_message(function_result_content.to_chat_message_content())

        print("CALL TOOL DONE")

    async def _call_llm(self, execution_state: SynapseExecutionState):
        history: ChatHistory = execution_state.runtime_data["history"]
        _logger.info(f"Calling LLM {datetime.now().second}")
        result = await self._llm.get_chat_message_content(
            chat_history=history,
            settings=self._llm_settings,
            kernel=self._kernel,
        )
        _logger.info(f"LLM returned response {datetime.now().second}")
        if result is not None:
            history.add_message(result)

