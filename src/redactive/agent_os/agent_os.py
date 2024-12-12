from contextlib import asynccontextmanager

from redactive.agent_os.runtime.agent_os_thread import AgentOSThread
from redactive.agent_os.runtime.semantic_kernel.runtime import SemanticKernelRuntime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.tools.generic_http_tool import GenericHttpTool
from redactive.agent_os.tools.protocol import Tool

_all_tools: list[Tool] = [
    GenericHttpTool()
]

_all_agents: list[OAgentSpec] = [
    OAgentSpec.model_validate_json(json_data=
    """
    {
        "uri": "http://localhost:8000/internet_reader",
        "description": "An agent that can browse the internet",
        "owner": "demo-user",
        "intent": "You are a helper agent that can browse the internet for a user and extract information to help them",
        "capabilities": {
            "generic_http_tool": {
                "user_identity": false
            }
        }                              
    }
    """
    )
]

global agent_os
agent_os = AgentOSThread(runtime_type=SemanticKernelRuntime, tools=_all_tools, agents=_all_agents)

@asynccontextmanager
async def start_runtime(app):
    agent_os.start()
    yield
    agent_os.stop()
