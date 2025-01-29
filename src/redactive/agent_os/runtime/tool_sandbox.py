from collections import Counter

from redactive.agent_os.runtime.assertions import run_cel_assertion
from redactive.agent_os.runtime.credentials_store import CredentialsStore
from redactive.agent_os.runtime.errors import EngagementShortCircuited
from redactive.agent_os.spec.agent import Capability
from redactive.agent_os.spec.engagements import EngagementRuntimeData, EngagementState
from redactive.agent_os.tools.protocol import Tool, ToolWithUserIdentity


class ToolSandbox:
    def __init__(self):
        self._creds = CredentialsStore()

    def get_additional_user_consent_required(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
    ) -> str | None:
        """Returns None if identity is ready to go!"""

    async def invoke_tool(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
        inputs: dict,
    ) -> dict:
        if self._should_short_circuit(
            engagement=engagement,
            tool=tool
        ):
            engagement.error = True
            raise EngagementShortCircuited()

        capability_use = EngagementState.CapabilityUse(
            inputs=inputs,
            inputs_allowed=False,
            success=False,
            outputs_allowed=False,
            outputs={},
        )
        engagement.state.history_names.append(tool.name)
        engagement.state.history[tool.name].append(capability_use)

        if not self._assert_input_restriction(
            engagement_state=engagement.state,
            capability=engagement.oagent.capabilities[tool.name],
            inputs=inputs,
        ):
            return {
                "error": "Those inputs are not allowed. You may try again with different parameters."
            }
        
        capability_use.inputs_allowed = True

        if engagement.oagent.capabilities[tool.name].user_identity:
            assert isinstance(tool, ToolWithUserIdentity)
            if not self._creds.has_user_creds(tool_name=tool.name, user_id=engagement.state.user.id):
                url, state = tool.get_user_signin_redirect()
                self._creds.set_sigin_state(tool_name=tool.name, user_id=engagement.state.user.id, state=state)
                return {
                    "error": "User consent required. Please ask them to follow this link",
                    "consent_link": url
                }
            else:
                inputs["access_token"] = self._creds.get_user_creds(tool_name=tool.name, user_id=engagement.state.user.id)
        elif (static_id := engagement.oagent.capabilities[tool.name].static_identity) is not None:
            inputs["access_token"] = self._creds.get_static_creds(tool_name=tool.name, static_id=static_id)

        try:
            results = await tool(**inputs)
        except Exception as e:
            return {
                "error": str(e)
            }
        else:
            capability_use.success = True

        if not self._assert_output_restriction(
            engagement_state=engagement.state,
            capability=engagement.oagent.capabilities[tool.name],
            outputs=results,
        ):
            return {
                "error": "Those inputs are not allowed. You may try again with different parameters."
            }

        capability_use.outputs = results
        capability_use.outputs_allowed = True
        
        # Only update recent if successful!
        engagement.state.inputs = {}
        engagement.state.outputs = {}
        engagement.state.recent_name = tool.name
        engagement.state.recent[tool.name] = capability_use

        return results

    @staticmethod
    def _should_short_circuit(
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
                    return True
        return False

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
        
        # capability_use = EngagementState.CapabilityUse(
        #     inputs=engagement_state.inputs,
        #     inputs_allowed=
        #     outputs=engagement_state.outputs,
        # )
        engagement_state.inputs = {}
        engagement_state.outputs = {}

        engagement_state.recent_name = tool_or_agent_name
        engagement_state.recent[tool_or_agent_name] = capability_use
        engagement_state.history_names.append(tool_or_agent_name)
        engagement_state.history[tool_or_agent_name].append(capability_use)
