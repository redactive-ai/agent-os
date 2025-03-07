import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.engagements import Engagement, EngagementRuntimeData

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engagements/{engagement_id}", tags=["engagements"])


@router.get("/", response_model_exclude_defaults=True)
async def get_engagement(engagement_id: str) -> Engagement:
    try:
        return agent_os.get_engagement(engagement_id=engagement_id)
    except KeyError:
        raise HTTPException(status_code=404)

@router.post("/", response_model_exclude_defaults=True)
async def append_engagement(engagement_id: str, text: Annotated[str, Body()]) -> Engagement:
    try:
        agent_os.append_to_engagement(engagement_id=engagement_id, text=text)
    except KeyError:
        raise HTTPException(status_code=404)
    return agent_os.get_engagement(engagement_id=engagement_id)

@router.get("/audit", response_model_exclude_defaults=True)
async def get_engagement_runtime_data(engagement_id: str) -> EngagementRuntimeData:
    try:
        return agent_os.get_engagement_runtime_data(engagement_id=engagement_id)
    except KeyError:
        raise HTTPException(status_code=404)
