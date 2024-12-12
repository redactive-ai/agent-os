
from collections.abc import Callable

from redactive.agent_os.spec.agent import AgentCapabilityRestriction
from redactive.agent_os.tools.protocol import Tool


class ToolSandbox:
    call: Callable

    def __init__(self, tool: Tool, restrictions: AgentCapabilityRestriction):
        self._tool = tool
        setattr(self, "call", self._tool)
        # functools.update_wrapper(self.call, self._tool)
        
    @property
    def name(self):
        return self._tool.id

    @property
    def description(self):
        return self._tool.description
