
import logging
from datetime import datetime

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.utils.logging import setup_logging

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

        for id_, capability in self._agent_spec.capabilities.items():
            tool = [t for t in tools if t.id == id_]
            if len(tool) < 0:
                raise NotImplementedError(f"Agent OS does not know about tool '{id_}'")
            
            # TODO: filter to only the tools specified in the agent spec
            sandbox = ToolSandbox(tool=tool[0], restrictions=capability.restrictions)
            kernel_func = kernel_function(func=sandbox.call, name=sandbox.name, description=sandbox.description)
            self._kernel.add_function(plugin_name=sandbox.name, function=kernel_func)

        # TODO: understand settings:
        self._llm_settings = self._kernel.get_prompt_execution_settings_from_service_id("chat")
        self._llm_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
    async def process(self, execution_data: SynapseExecutionState):
        chat_history: ChatHistory = execution_data.runtime_data["history"]
        _logger.info(f"Calling LLM {datetime.now().second}")
        result = await self._llm.get_chat_message_content(
            chat_history=chat_history,
            settings=self._llm_settings,
            kernel=self._kernel,
        )
        _logger.info(f"LLM returned response {datetime.now().second}")
        if result is not None:
            chat_history.add_message(result)
