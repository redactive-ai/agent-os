from contextlib import asynccontextmanager

from redactive.agent_os.runtime.agent_os_thread import AgentOSThread
from redactive.agent_os.runtime.semantic_kernel.runtime import SemanticKernelRuntime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.tools.json_http_tool import JsonHttpTool
from redactive.agent_os.tools.protocol import Tool

_all_tools: list[Tool] = [
    JsonHttpTool()
]

_default_agents: list[OAgentSpec] = [
    OAgentSpec.model_validate_json(json_data=
    """
    {
        "name": "internet_reader",
        "description": "An agent that can browse the internet",
        "owner": "demo-user",
        "intent": "You are a helper agent that can browse the internet for a user and extract information to help them",
        "capabilities": {
            "generic_http_tool": {
                "user_identity": false,
                "input_restriction": {
                    "assert": "tools.generic_http_tool.inputs.url.startsWith('https://www.reddit.com/')"
                }
            }
        }
    }
    """
    )
]
# "assert": "tools.generic_http_tool.inputs.url.startsWith('https://www.reddit.com/')"

global agent_os
agent_os = AgentOSThread(runtime_type=SemanticKernelRuntime, tools=_all_tools)

@asynccontextmanager
async def start_runtime(app):
    agent_os.start()

    for default_agent in _default_agents:
        agent_os.update_agent(agent=default_agent)

    yield
    agent_os.stop()
