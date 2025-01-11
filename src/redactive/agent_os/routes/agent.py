import logging
from typing import Annotated

from fastapi import APIRouter, Body, Header, HTTPException
from fastapi.responses import RedirectResponse

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import EngagementUser

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agent"])

@router.get("/")
async def list_agents():
    return [dict(name=a.name, description=a.description) for a in agent_os.list_all_agents()]

@router.post("/update-agent")
async def update_agent(agent: Annotated[OAgentSpec, Body()]):
    agent_os.update_agent(agent=agent)
    return agent.name


@router.get("/{agent_name}", response_model_exclude_defaults=True)
async def get_agent(agent_name: str):
    try:
        return agent_os.get_agent_by_reference(agent_ref=agent_name)
    except KeyError:
        raise HTTPException(status_code=404)


@router.post("/{agent_name}")
async def trigger_agent(agent_name: str, calling_user_id: Annotated[str, Header()], text: Annotated[str | None, Body()] = None) -> RedirectResponse:
    user = EngagementUser(
        id=calling_user_id,
        email=f"{calling_user_id}@redactive.ai"
    )

    try:
        agent = agent_os.get_agent_by_reference(agent_ref=agent_name)
    except KeyError:
        raise HTTPException(status_code=404)
    
    engagement_id = agent_os.create_engagement(agent=agent, user=user)
    if text:
        agent_os.append_to_engagement(engagement_id=engagement_id, text=text)
    return RedirectResponse(f"/engagements/{engagement_id}/", status_code=303)