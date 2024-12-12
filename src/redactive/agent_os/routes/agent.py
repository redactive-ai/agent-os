
import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse

from redactive.agent_os.agent_os import agent_os

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agent"])


@router.get("/{agent_id}")
async def get_agent(agent_id: str, text: Annotated[str | None, Query()] = None):
    try:
        agent = agent_os.get_agent_by_id(agent_id=agent_id)
    except KeyError:
        raise HTTPException(status_code=404)
    
    if text is None:
        return agent
    
    else:
        syn_id = agent_os.trigger_agent(agent=agent, text=text)
        return RedirectResponse(f"/api/synapses/{syn_id}/", status_code=303)

@router.post("/{agent_id}")
async def trigger_agent(agent_id: str, text: Annotated[str, Body()]) -> RedirectResponse:
    try:
        agent = agent_os.get_agent_by_id(agent_id=agent_id)
    except KeyError:
        raise HTTPException(status_code=404)
    
    syn_id = agent_os.trigger_agent(agent=agent, text=text)
    return RedirectResponse(f"/api/synapses/{syn_id}/", status_code=303)