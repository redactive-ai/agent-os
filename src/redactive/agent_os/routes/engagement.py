import logging

from fastapi import APIRouter, HTTPException

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engagements/{engagement_id}", tags=["engagements"])


@router.get("/")
async def get_SynapseExecutionState_state(engagement_id: str) -> Engagement:
    try:
        return agent_os.get_engagement(engagement_id=engagement_id)
    except KeyError:
        raise HTTPException(status_code=404)

@router.get("/audit")
async def iterate_SynapseExecutionState(engagement_id: str) -> EngagementRuntimeData:
    return agent_os.get_engagement_runtime_data(engagement_id=engagement_id)
