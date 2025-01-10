

from typing import Annotated

import httpx

from redactive.agent_os.secrets import get_secret
from redactive.agent_os.tools.protocol import Tool


class BingSearch(Tool):
    @property
    def name(self) -> str:
        return "bing_search_tool"
    
    @property
    def description(self) -> str:
        return "Perform a bing internet search"

    async def __call__(self, query: Annotated[str, "search query"]) -> str:
        client = httpx.AsyncClient(
            base_url="https://api.bing.microsoft.com/v7.0/search",
            headers={
                "Ocp-Apim-Subscription-Key": get_secret("bing_search__api_key"),
            },
            params={
                "textDecorations": True,
                "textFormat": "HTML",
            }
        )

        response = await client.get("", params={"q": query})

        return response.json()