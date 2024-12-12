
import logging

from fastapi import APIRouter, HTTPException

from redactive.agent_os.agent_os import agent_os
from redactive.agent_os.spec.synapse import SynapseExecutionState, SynapseStatus

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/synapses/{synapse_id}", tags=["synapse"])


@router.get("/")
async def get_synapse_state(synapse_id: str) -> SynapseStatus:
    try:
        return agent_os.get_synapse_status(syn_id=synapse_id)
    except KeyError:
        raise HTTPException(status_code=404)

@router.get("/audit")
async def iterate_synapse(synapse_id: str) -> SynapseExecutionState:
    return agent_os.get_synapse_execution_state(syn_id=synapse_id)
