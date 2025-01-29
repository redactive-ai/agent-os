from contextlib import asynccontextmanager

from redactive.agent_os.runtime.agent_os_thread import AgentOSThread
from redactive.agent_os.runtime.semantic_kernel.runtime import SemanticKernelRuntime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.tools.bing_search_tool import BingSearchTool
from redactive.agent_os.tools.google_calendar_tool import GoogleCalendarTool
from redactive.agent_os.tools.json_http_tool import JsonHttpTool
from redactive.agent_os.tools.protocol import Tool

_all_tools: list[Tool] = [
    JsonHttpTool(),
    BingSearchTool(),
    GoogleCalendarTool(),
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
            "json_http_tool": {
                "user_identity": false
            }
        },
        "exposes": {
            "urls_accessed": "history.json_http_tool.map(t, t.inputs.url)"
        }
    }
    """),
    OAgentSpec.model_validate_json(json_data=
    """
    {
        "name": "reddit_reader_insecure",
        "description": "An agent that can only browse reddit, but may try not to",
        "owner": "demo-user",
        "intent": "You are a helper agent that can browse reddit for a user and extract information to help them. You may only browse reddit",
        "capabilities": {
            "json_http_tool": {
                "user_identity": false
            }
        },
        "exposes": {
            "urls_accessed": "history.json_http_tool.map(t, [t.inputs.url, t.inputs_allowed])"
        },
        "lifespan": {
            "short_circuit": 2
        }
    }
    """),
    OAgentSpec.model_validate_json(json_data=
    """
    {
        "name": "reddit_reader_secure",
        "description": "An agent that can only browse reddit",
        "owner": "demo-user",
        "intent": "You are a helper agent that can browse reddit for a user and extract information to help them. You may only browse reddit",
        "capabilities": {
            "json_http_tool": {
                "user_identity": false,
                "input_restriction": {
                    "assertion": "inputs.url.startsWith('https://www.reddit.com/') || inputs.url.startsWith('https://api.reddit.com/')"
                }
            }
        },
        "exposes": {
            "urls_accessed": "history.json_http_tool.map(t, [t.inputs.url, t.inputs_allowed])"
        },
        "lifespan": {
            "short_circuit": 2
        }
    }
    """),
]

global agent_os
agent_os = AgentOSThread(runtime_type=SemanticKernelRuntime, tools=_all_tools)

@asynccontextmanager
async def start_runtime(app):
    agent_os.start()

    for default_agent in _default_agents:
        agent_os.update_agent(agent=default_agent)

    yield
    agent_os.stop()
