import logging

from click import Group

from redactive.agent_os.config import AgentOSConfig
from redactive.agent_os.server import build_server
from redactive.utils.servers import run_app_with_uvicorn

logger = logging.getLogger(__name__)


def add_agent_os_commands(cli: Group):
    @cli.command()
    def serve():
        agent_os = build_server()
        logger.debug("Initialized Management Server")
        run_app_with_uvicorn(app=agent_os, port=AgentOSConfig().port)
