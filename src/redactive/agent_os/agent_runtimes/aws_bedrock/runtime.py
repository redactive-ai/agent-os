import logging
from datetime import UTC, datetime

import boto3

from redactive.agent_os.runtime_protocols import AgentRuntime
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData, EngagementState, EngagementUser
from redactive.utils.random_gen import random_alpha_numeric_string

_logger = logging.getLogger(__name__)

class AWSBedrockRuntime(AgentRuntime):
    _executions: dict[str, EngagementRuntimeData]

    def __init__(self):
        self._executions = {}
        boto3_session = boto3.Session(profile_name="AdministratorAccess-637423639316")
        self._client = boto3_session.client(
            service_name="bedrock-agent", region_name="ap-southeast-2"
        )
        self._runtime_client = boto3_session.client(
            service_name="bedrock-agent-runtime", region_name="ap-southeast-2"
        )

    def get_oagent_spec(self, agent_name: str) -> OAgentSpec:
        aws_agent_id, aws_agent_alias_id = agent_name.split(":")
        aws_agent = self._client.get_agent(aws_agent_id)
        return aws_agent["agent"]

    def list_all_agents(self) -> list[OAgentSpec]:
        return self._client.list_agents()


    def create_engagement(self, agent_name: str, user: EngagementUser) -> str:
        oagent = self.get_oagent_spec(agent_name=agent_name)
        # TODO: ensure oagent spec is fulfillable by this runtime
        eng_id = random_alpha_numeric_string(8)

        execution_data = EngagementRuntimeData(
            engagement_id=eng_id,
            oagent=oagent,
            state=EngagementState(
                time_started=datetime.now(UTC),
                time_now=datetime.now(UTC),
                user=EngagementUser(
                    id=user.id,
                    email=user.email,
                ),
                recent={cap: None for cap in oagent.capabilities.keys()},
                history={cap: [] for cap in oagent.capabilities.keys()}
            ),
            internal=dict(history=[])
        )
        self._executions[eng_id] = execution_data
        return eng_id
    
    def append_to_engagement(self, engagement_id: str, text: str) -> None:
        engagement = self._executions[engagement_id]
        engagement.internal["history"].append(text)
        engagement.state.history_names.append("+external_input")

    @staticmethod
    def _parse_state(data: EngagementRuntimeData) -> Engagement.Status:
        if data.error:
            return Engagement.Status.ERROR
        
        history: ChatHistory = data.internal["history"]
        last_message = history.messages[-1]
        if last_message.finish_reason == "stop":
            return Engagement.Status.COMPLETE
        if last_message.finish_reason == "TOOL":
            return Engagement.Status.AWAITING_TOOL
        return Engagement.Status.AWAITING_LLM

    @staticmethod
    def _parse_results(data: EngagementRuntimeData) -> dict:
        results = {}
        chat_history: ChatHistory = data.internal["history"]
        for expose_key, expose_cel in data.oagent.exposes.items():
            result_value = run_cel_assertion(data.state, expose_cel)
            results[expose_key] = result_value
        results["text"] = chat_history.messages[-1].content
        return results

    def get_engagement_runtime_data(self, engagement_id: str) -> EngagementRuntimeData:
        return self._executions[engagement_id]

    def get_engagement(self, engagement_id: str) -> Engagement:
        runtime_data = self._executions[engagement_id]
        status = self._parse_state(runtime_data)

        return Engagement(
            engagement_id=engagement_id,
            oagent=runtime_data.oagent,
            user=runtime_data.state.user,
            status=status,
            results=self._parse_results(runtime_data) if status is Engagement.Status.COMPLETE else None
        )

    async def process_engagement(self, engagement_id: str) -> None:
        runtime_data = self._executions[engagement_id]
        
        if not runtime_data.error:
            try:
                response = self._runtime_client.invoke_agent(
                    agentId="4JYJWWIQWT",
                    agentAliasId="XTOJKNTGYQ",
                    sessionId=engagement_id,
                    inputText=runtime_data.internal["history"][-1],
                )
                for event in response.get("completion"):
                    print(event)
                    chunk = event["chunk"]
                    completion = completion + chunk["bytes"].decode()

            except Exception as exc:
                _logger.error("Engagement Error: %s", exc, exc_info=True)
                runtime_data.error = True