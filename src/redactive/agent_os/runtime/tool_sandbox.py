from collections import Counter

from redactive.agent_os.runtime.assertions import run_cel_assertion
from redactive.agent_os.runtime.credentials_store import CredentialsStore
from redactive.agent_os.spec.agent import Capability
from redactive.agent_os.spec.engagements import EngagementRuntimeData, EngagementState
from redactive.agent_os.tools.protocol import Tool, ToolWithUserIdentity


class ToolSandbox:
    def __init__(self):
        self._creds = CredentialsStore()

    def should_short_circuit(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
    ) -> bool:
        """True if short circuit has been reached, engagement MUST end immediately"""
        engagement.capability_attempt_history.append(tool.name)
        if (engagement.oagent.lifespan is not None and engagement.oagent.lifespan.short_circuit is not None):
            for sub_sequence_length in range(1, len(engagement.capability_attempt_history) + 1):
                counts_of_sub_sequences = Counter(zip(*(engagement.capability_attempt_history[i:] for i in range(sub_sequence_length))))
                _most_common_seq, most_common_count = counts_of_sub_sequences.most_common(1)[0]
                if most_common_count > engagement.oagent.lifespan.short_circuit:
                    engagement.error = True
                    return True
        return False

    def get_additional_user_consent_required(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
    ) -> str | None:
        """Returns None if identity is ready to go!"""
        if engagement.oagent.capabilities[tool.name].user_identity:
            assert isinstance(tool, ToolWithUserIdentity)

            if self._creds.has_user_creds(tool_name=tool.name, user_id=engagement.state.user.id):
                return None
            else:
                url, state = tool.get_user_signin_redirect()
                self._creds.set_sigin_state(tool_name=tool.name, user_id=engagement.state.user.id, state=state)
                return f"Please go to this url to authorize the agent using this tool on your behalf: {url}"
        return None

    async def invoke_tool(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
        inputs: dict,
    ) -> dict:
        if not self._assert_input_restriction(
            engagement_state=engagement.state,
            capability=engagement.oagent.capabilities[tool.name],
            inputs=inputs,
        ):
            return {
                "error": "Those inputs are not allowed. You may try again with different parameters."
            }

        if engagement.oagent.capabilities[tool.name].user_identity:
            inputs["access_token"] = self._creds.get_user_creds(tool_name=tool.name, user_id=engagement.state.user.id)
        elif (static_id := engagement.oagent.capabilities[tool.name].static_identity) is not None:
            inputs["access_token"] = self._creds.get_static_creds(tool_name=tool.name, static_id=static_id)

        results = await tool(**inputs)

        if not self._assert_output_restriction(
            engagement_state=engagement.state,
            capability=engagement.oagent.capabilities[tool.name],
            outputs=results,
        ):
            return {
                "error": "Those inputs are not allowed. You may try again with different parameters."
            }

        self._update_engagement_state_history(
            engagement_state=engagement.state,
            tool_or_agent_name=tool.name,
        )

        return results

    @staticmethod
    def _assert_input_restriction(
        engagement_state: EngagementState,
        capability: Capability,
        inputs: dict,
    ) -> bool:
        """Only updates the "inputs" of the engagement state, and returns whether the capability is allowed (restriction is met if set)"""
        engagement_state.inputs = inputs
        return (
            capability.input_restriction is None
            or capability.input_restriction.assertion is None
            or run_cel_assertion(engagement_state, capability.input_restriction.assertion)
        )
    
    @staticmethod
    def _assert_output_restriction(
        engagement_state: EngagementState,
        capability: Capability,
        outputs: dict,
    ) -> bool:
        """Updates the "outputs" of the engagement in place, and returns whether the capability is allowed (restriction is met if set)"""
        engagement_state.outputs = outputs
        return (
            capability.output_restriction is None
            or capability.output_restriction.assertion is None
            or run_cel_assertion(engagement_state, capability.output_restriction.assertion)
        )

    @staticmethod
    def _update_engagement_state_history(
        engagement_state: EngagementState,
        tool_or_agent_name: str,
    ) -> None:
        """Updates the recent & history fields of the engagement in place, and resets the inputs & outputs. Should only be called after successful invocations."""
        
        capability_use = EngagementState.CapabilityUse(inputs=engagement_state.inputs, outputs=engagement_state.outputs)
        engagement_state.inputs = {}
        engagement_state.outputs = {}

        engagement_state.recent_name = tool_or_agent_name
        engagement_state.recent[tool_or_agent_name] = capability_use
        engagement_state.history_names.append(tool_or_agent_name)
        engagement_state.history[tool_or_agent_name].append(capability_use)
