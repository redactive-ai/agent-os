
from pydantic import BaseModel


class AgentOSConfig(BaseModel):
    # CONFIG_SECTION = "agent_os"

    port: int = 8000
    base_uri: str = "http://localhost:8000"
    dashboard_dir: str | None = None
    allow_localhost_cors: bool = False