import asyncio
from threading import Thread

from redactive.agent_os.runtime_protocols import AgentRuntime, MutableAgentRuntime, ToolRuntime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData, EngagementUser


class AgentOSThread(Thread):
    _agent_runtime_type: type[AgentRuntime]

    _running: bool
    _eng_ids: list[str]
    _agent_runtime: AgentRuntime
    _tool_runtime: ToolRuntime | None

    def __init__(self, agent_runtime_type: type[AgentRuntime]):
        self._agent_runtime_type = agent_runtime_type

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

        self._agent_runtime = self._agent_runtime_type()

        while self._running:
            for engagement_id in self._eng_ids:
                await self._agent_runtime.process_engagement(engagement_id=engagement_id)

            await asyncio.sleep(0)

    def stop(self):
        self._running = False

    def update_agent(self, agent: OAgentSpec) -> None:
        assert isinstance(self._agent_runtime_type, MutableAgentRuntime)
        self.update_agent(agent)

    def get_agent_by_reference(self, agent_ref: str) -> OAgentSpec:
        agent_name = agent_ref.replace("oagent://", "")
        return self._agent_runtime.get_oagent_spec(agent_name)

    # def get_tool_or_agent_by_reference(self, reference: str) -> Tool | OAgentSpec:
    #     if reference.startswith("oagent://"):
    #         return self.get_agent_by_reference(reference)
    #     else:
    #         # Preference tools
    #         if reference in self._all_tools:
    #             return self._all_tools[reference]
    #         else:
    #             return self._all_agents[reference]
            
    def list_all_agents(self) -> list[OAgentSpec]:
        return self._agent_runtime.list_all_agents()

    def create_engagement(self, agent_name: str, user: EngagementUser) -> str:
        engagement_id = self._agent_runtime.create_engagement(agent_name=agent_name, user=user)
        self._eng_ids.append(engagement_id)
        return engagement_id
    
    def append_to_engagement(self, engagement_id: str, text: str) -> None:
        self._agent_runtime.append_to_engagement(engagement_id=engagement_id, text=text)

    def get_engagement(self, engagement_id: str) -> Engagement:
        return self._agent_runtime.get_engagement(engagement_id=engagement_id)

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData:
        return self._agent_runtime.get_engagement_runtime_data(engagement_id=engagement_id)
