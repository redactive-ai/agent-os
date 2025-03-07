
from redactive.agent_os.native_tools.bing_search_tool import BingSearchTool
from redactive.agent_os.native_tools.google_calendar_tool import GoogleCalendarTool
from redactive.agent_os.native_tools.json_http_tool import JsonHttpTool
from redactive.agent_os.native_tools.protocol import Tool
from redactive.agent_os.runtime_protocols import ToolRuntime


class NativeToolRuntime(ToolRuntime):
    _all_tools: list[Tool]

    def __init__(self):
        self._all_tools = [
            JsonHttpTool(),
            BingSearchTool(),
            GoogleCalendarTool(),
        ]

    # TODO: serialise tool name, description and parameters in a not-runtime-specific way
    def get_tool_by_name(self, tool_name: str) -> Tool:
        matching_tools = [t for t in self._all_tools if t.name == tool_name]
        if len(matching_tools) > 0:
            return matching_tools[0]
        raise KeyError(f"No tool configured in runtime with name '{tool_name}'")

    async def invoke_tool(
        self,
        tool_name: str,
        inputs: dict,
    ) -> dict:
        tool = self.get_tool_by_name(tool_name=tool_name)
        try:
            return await tool(**inputs)
        except Exception as e:
            return {
                "error": str(e)
            }
