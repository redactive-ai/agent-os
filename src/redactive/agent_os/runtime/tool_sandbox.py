from redactive.agent_os.runtime.assertions import run_cel_assertion
from redactive.agent_os.runtime.credentials_store import CredentialsStore
from redactive.agent_os.runtime.errors import RestrictedToolInput, RestrictedToolOutput
from redactive.agent_os.spec.agent import Capability
from redactive.agent_os.spec.engagements import EngagementRuntimeData, EngagementState
from redactive.agent_os.tools.protocol import Tool, ToolWithUserIdentity


class ToolSandbox:
    def __init__(self):
        self._creds = CredentialsStore()

    def validate_inputs(
        self,
        engagement: EngagementRuntimeData,
        tool: Tool,
        desired_inputs: dict,
    ) -> bool:
        # TODO: should it be possible to to validate inputs without mutating engagement?
        return self._update_engagement_input_and_assert_restriction(
            engagement_state=engagement.state,
            tool_or_agent_name=tool.name,
            capability=engagement.oagent.capabilities[tool.name],
            inputs=desired_inputs,
        )
        

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
        if not self._update_engagement_input_and_assert_restriction(
            engagement_state=engagement.state,
            tool_or_agent_name=tool.name,
            capability=engagement.oagent.capabilities[tool.name],
            inputs=inputs,
        ):
            raise RestrictedToolInput()

        if engagement.oagent.capabilities[tool.name].user_identity:
            inputs["access_token"] = self._creds.get_user_creds(tool_name=tool.name, user_id=engagement.state.user.id)
        elif (static_id := engagement.oagent.capabilities[tool.name].static_identity) is not None:
            inputs["access_token"] = self._creds.get_static_creds(tool_name=tool.name, static_id=static_id)

        results = await tool(**inputs)

        if not self._update_engagement_output_and_assert_restriction(
            engagement_state=engagement.state,
            tool_or_agent_name=tool.name,
            capability=engagement.oagent.capabilities[tool.name],
            outputs=results,
        ):
            raise RestrictedToolOutput()

        return results

    @staticmethod
    def _update_engagement_input_and_assert_restriction(
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
    def _update_engagement_output_and_assert_restriction(
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