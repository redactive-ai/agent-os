import asyncio
from threading import Thread

from redactive.agent_os.runtime.runtime_protocol import Runtime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.synapse import SynapseExecutionState, SynapseStatus
from redactive.agent_os.tools.protocol import Tool


class AgentOSThread(Thread):
    _runtime_type: type[Runtime]
    _all_tools: list[Tool]
    """Dict of all known tool specs by uri"""
    _all_agents: list[OAgentSpec]
    """Dict of all known agent specs by uri"""

    _running: bool
    _syn_ids: list[str]
    _runtime: Runtime

    def __init__(self, runtime_type: type[Runtime], tools: list[Tool], agents: list[OAgentSpec]):
        self._runtime_type = runtime_type
        self._all_tools = tools
        self._all_agents = agents

        self._running: bool = False
        self._syn_ids = []

        super().__init__(name="agent_runtime")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_async())
        loop.close()


    async def _run_async(self):
        self._running = True
        self._runtime = self._runtime_type(self._all_tools)

        while self._running:
            for syn_id in self._syn_ids:
                await self._runtime.process_synapse(syn_id=syn_id)
            await asyncio.sleep(1)

    def stop(self):
        self._running = False

    def get_agent_by_id(self, agent_id: str) -> OAgentSpec:
        matching = [a for a in self._all_agents if a.uri.path.lstrip("/") == agent_id]
        if len(matching) < 1:
            raise KeyError(f"No agent matching id {agent_id}")
        return matching[0]

    def get_tool_or_agent(self, id: str) -> Tool | OAgentSpec:
        if id.startswith("oagent://"):
            raise NotImplementedError()
        else:
            matching = [t for t in self._all_tools if t.id == id]
            if len(matching) < 1:
                raise KeyError(f"No tool matching id {id}")
            return matching[0]

    def trigger_agent(self, agent: OAgentSpec, text: str | None) -> str:
        syn_id = self._runtime.trigger_agent(
            oagent=agent,
            text=text
        )
        self._syn_ids.append(syn_id)
        return syn_id

    def get_synapse_status(self, syn_id: str) -> SynapseStatus:
        return self._runtime.get_synapse_status(syn_id=syn_id)

    def get_synapse_execution_state(self, syn_id: str) -> SynapseExecutionState:
        return self._runtime.get_synapse_execution_state(syn_id=syn_id)
