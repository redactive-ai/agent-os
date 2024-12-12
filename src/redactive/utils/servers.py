import logging
from asyncio import run
from functools import wraps

import uvicorn
from fastapi import FastAPI

logger = logging.getLogger(__name__)


def run_synchronously(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return run(func(*args, **kwargs))

    return wrapper


def run_app_with_uvicorn(app: FastAPI, port: int):
    custom_params = {}
    # log_config = get_uvicorn_log_config()
    log_config = None
    if log_config:
        custom_params["log_config"] = log_config

    uvicorn.run(app, host="0.0.0.0", loop="uvloop", port=port, **custom_params)
