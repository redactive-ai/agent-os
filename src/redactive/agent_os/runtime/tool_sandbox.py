from redactive.agent_os.runtime.assertions import run_cel_assertion
from redactive.agent_os.spec.agent import Capability
from redactive.agent_os.spec.engagements import EngagementState


class ToolSandbox:
    @staticmethod
    def update_engagement_input_and_assert_restriction(
        engagement_state: EngagementState,
        tool_or_agent_name: str,
        capability: Capability,
        inputs: dict,
    ) -> bool:
        """Updates the engagement state in place, and returns whether the capability is allowed (restriction is met if set)"""
        engagement_state.recent_name = tool_or_agent_name
        capability_use = EngagementState.CapabilityUse(inputs=inputs, outputs=None)
        
        engagement_state.recent[tool_or_agent_name] = capability_use
        engagement_state.history_names.append(tool_or_agent_name)
        if tool_or_agent_name not in engagement_state.history:
            engagement_state.history[tool_or_agent_name] = []
        engagement_state.history[tool_or_agent_name].append(capability_use)

        return (
            capability.input_restriction is None
            or capability.input_restriction.assertion is None
            or run_cel_assertion(engagement_state, capability.input_restriction.assertion)
        )
    
    @staticmethod
    def update_engagement_output_and_assert_restriction(
        engagement_state: EngagementState,
        tool_or_agent_name: str,
        capability: Capability,
        outputs: dict,
    ) -> bool:
        """Updates the engagement state in place, and returns whether the capability is allowed (restriction is met if set)"""
        engagement_state.recent[tool_or_agent_name].outputs = outputs
        engagement_state.history[tool_or_agent_name][-1].outputs = outputs

        return (
            capability.output_restriction is None
            or capability.output_restriction.assertion is None
            or run_cel_assertion(engagement_state, capability.output_restriction.assertion)
        )