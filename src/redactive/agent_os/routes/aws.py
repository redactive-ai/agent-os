import logging

import boto3
import boto3.session
from botocore.exceptions import ClientError
from fastapi import APIRouter

from redactive.utils.random_gen import random_alpha_numeric_string

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aws", tags=["aws"])

@router.get("/invoke-aws-agent")
async def test_invoke_aws_agent():
    session_id = random_alpha_numeric_string(8)
    boto3_session = boto3.Session(profile_name="AdministratorAccess-637423639316")
    runtime_client = boto3_session.client(
        service_name="bedrock-agent-runtime", region_name="ap-southeast-2"
    )
    try:
        response = runtime_client.invoke_agent(
            agentId="4JYJWWIQWT",
            agentAliasId="XTOJKNTGYQ",
            sessionId=session_id,
            inputText="whats the current btc price?",
        )

        runtime_client.get

        completion = ""

        print(response)

        for event in response.get("completion"):
            print(event)
            chunk = event["chunk"]
            completion = completion + chunk["bytes"].decode()

    except ClientError as e:
        _logger.error(f"Couldn't invoke agent. {e}")
        raise

    return completion


