import asyncio
import logging

import click
import uvloop

from redactive.cli.agent_os import add_agent_os_commands

logger = logging.getLogger(__name__)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@click.group()
def cli():
    logging.getLogger("redactive").setLevel(logging.DEBUG)
    pass


@cli.group()
def agent_os():
    pass


add_agent_os_commands(agent_os)



if __name__ == "__main__":
    cli()
