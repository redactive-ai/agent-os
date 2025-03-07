import logging
from typing import Annotated

from fastapi import APIRouter, Body, Header, HTTPException
from fastapi.responses import RedirectResponse

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.agent import OAgentSpec
from redactive.agent_os.spec.engagements import EngagementUser

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["security"])

@router.get("/blocked-tools")
async def list_blocked_tools():
    return [dict(name=a.name, description=a.description) for a in agent_os.list_all_agents()]