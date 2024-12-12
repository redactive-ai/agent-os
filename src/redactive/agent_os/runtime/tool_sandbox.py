from cel import evaluate

from redactive.agent_os.spec.agent import AgentCapabilityRestriction
from redactive.agent_os.spec.synapse import Synapse


class ToolSandbox:
    @staticmethod
    def assert_synapse(restriction: AgentCapabilityRestriction | None, synapse: Synapse) -> bool:
        return restriction is None or restriction.assert_ is None or evaluate(restriction.assert_, synapse.model_dump(by_alias=True))
