from cel import evaluate

from redactive.agent_os.spec.agent import AgentCapabilityRestriction
from redactive.agent_os.spec.engagements import EngagementState


class ToolSandbox:
    @staticmethod
    def assert_restriction(restriction: AgentCapabilityRestriction | None, engagement_state: EngagementState) -> bool:
        return restriction is None or restriction.assert_ is None or evaluate(restriction.assert_, engagement_state.model_dump(by_alias=True))
