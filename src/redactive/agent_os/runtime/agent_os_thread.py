import asyncio
import logging
from threading import Thread

from redactive.agent_os.runtime.runtime_protocol import Runtime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData
from redactive.agent_os.tools.protocol import Tool

_logger = logging.getLogger(__name__)


class AgentOSThread(Thread):
    _runtime_type: type[Runtime]
    _all_tools: dict[str, Tool]
    """Dict of all known tool specs by uri"""
    _all_agents: dict[str, OAgentSpec]
    """Dict of all known agent specs by uri"""

    _running: bool
    _eng_ids: list[str]
    _runtime: Runtime

    def __init__(self, runtime_type: type[Runtime], tools: list[Tool]):
        self._runtime_type = runtime_type
        self._all_tools = {t.name: t for t in tools}
        self._all_agents = {}

        self._running: bool = False
        self._eng_ids = []

        super().__init__(name="agent_runtime")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_async())
        loop.close()


    async def _run_async(self):
        self._running = True
        self._runtime = self._runtime_type(list(self._all_tools.values()))

        while self._running:
            for engagement_id in self._eng_ids:
                try:
                    await self._runtime.process_engagement(engagement_id=engagement_id)
                except Exception as exc:
                    _logger.error("Engagement Error: %s", exc, exc_info=True)

            await asyncio.sleep(0)

    def stop(self):
        self._running = False

    def update_agent(self, agent: OAgentSpec) -> None:
        self._all_agents[agent.name] = agent

    def get_agent_by_reference(self, agent_ref: str) -> OAgentSpec:
        agent_name = agent_ref.replace("oagent://", "")
        return self._all_agents[agent_name]

    def get_tool_or_agent_by_reference(self, reference: str) -> Tool | OAgentSpec:
        if reference.startswith("oagent://"):
            return self.get_agent_by_reference(reference)
        else:
            # Preference tools
            if reference in self._all_tools:
                return self._all_tools[reference]
            else:
                return self._all_agents[reference]
            
    def list_all_agents(self) -> list[OAgentSpec]:
        return list(self._all_agents.values())

    def trigger_agent(self, agent: OAgentSpec, text: str | None) -> str:
        syn_id = self._runtime.trigger_agent(
            oagent=agent,
            text=text
        )
        self._eng_ids.append(syn_id)
        return syn_id

    def get_engagement(self, engagement_id: str) -> Engagement:
        return self._runtime.get_engagement(engagement_id=engagement_id)

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData:
        return self._runtime.get_engagement_runtime_data(engagement_id=engagement_id)
