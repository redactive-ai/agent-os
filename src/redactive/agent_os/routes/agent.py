import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.agent import OAgentSpec

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agent"])

@router.get("/")
async def list_agents():
    return [dict(name=a.name, description=a.description) for a in agent_os.list_all_agents()]

@router.post("/update-agent")
async def update_agent(agent: Annotated[OAgentSpec, Body()]):
    agent_os.update_agent(agent=agent)
    return agent.name


@router.get("/{agent_name}")
async def get_agent(agent_name: str, text: Annotated[str | None, Query()] = None):
    try:
        agent = agent_os.get_agent_by_reference(agent_ref=agent_name)
    except KeyError:
        raise HTTPException(status_code=404)
    
    if text is None:
        return agent
    
    else:
        syn_id = agent_os.trigger_agent(agent=agent, text=text)
        return RedirectResponse(f"/engagements/{syn_id}/", status_code=303)

@router.post("/{agent_name}")
async def trigger_agent(agent_name: str, text: Annotated[str, Body()]) -> RedirectResponse:
    try:
        agent = agent_os.get_agent_by_reference(agent_ref=agent_name)
    except KeyError:
        raise HTTPException(status_code=404)
    
    syn_id = agent_os.trigger_agent(agent=agent, text=text)
    return RedirectResponse(f"/engagements/{syn_id}/", status_code=303)