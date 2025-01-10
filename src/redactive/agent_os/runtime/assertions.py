import logging
from typing import Any

from cel import evaluate

from redactive.agent_os.spec.engagements import EngagementState

_logger = logging.getLogger(__name__)


def run_cel_assertion(engagement_state: EngagementState, assertion: str) -> Any:
    try:
        return evaluate(assertion, engagement_state.model_dump(by_alias=True))
    except Exception as exc:
        _logger.error("Assertion Error: %s", exc, exc_info=True)
        return None