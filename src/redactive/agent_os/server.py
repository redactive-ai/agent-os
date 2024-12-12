import logging
from importlib.metadata import version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from redactive.agent_os.agent_os import start_runtime
from redactive.agent_os.config import AgentOSConfig
from redactive.agent_os.routes.agent import router as agent_router
from redactive.agent_os.routes.synapse import router as synapse_router

_logger = logging.getLogger(__name__)


def build_server():
    server = FastAPI(
        title="Redactive",
        description="Easily manage secure AI Agents",
        summary="Redactive Agent OS",
        redoc_url=None,
        responses={
            400: {"description": "Request was invalid"},
            401: {"description": "Request was missing required authentication"},
            403: {"description": "Request was missing required authorization"},
        },
        swagger_ui_parameters={},
        lifespan=start_runtime,
    )

    if AgentOSConfig().allow_localhost_cors:
        server.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://localhost:8001"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # The order the routers are added determines their order in the openapi spec, and consequently the docs order
    server.include_router(agent_router, prefix="/api")
    server.include_router(synapse_router, prefix="/api")

    # TODO: can this be removed?
    @server.get("/api/health", include_in_schema=False)
    def healthcheck():
        return {"status": "ok!"}

    @server.get("/api/build.json", include_in_schema=False)
    def build():
        return {"version": f"v{version('redactive-agent-os')}"}

    # if AgentOSConfig().dashboard_dir is not None:
    #     _logger.info("Serving static files from: %s", AgentOSConfig().dashboard_dir)
    #     server.mount("/", DashboardFiles(directory=AgentOSConfig().dashboard_dir), name="dashboard")
    # else:
    _logger.warning("No dashboard directory configured, skipping static file serving")

    return server
