

from typing import Annotated

import httpx

from redactive.agent_os.tools.protocol import Tool


class JsonHttpTool(Tool):
    @property
    def name(self) -> str:
        return "generic_http_tool"
    
    @property
    def description(self) -> str:
        return "Call any unauthenticated https endpoint"

    async def __call__(self, url: Annotated[str, "https endpoint to call"]) -> str:
        client = httpx.AsyncClient()
        response = await client.get(url=url)

        return response.json()