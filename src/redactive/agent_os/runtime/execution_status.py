
from enum import StrEnum


class ExecutionStatus(StrEnum):
    AWAITING_LLM = "awaiting-llm"
    AWAITING_TOOL = "awaiting-tool"
    AWAITING_VERIFICATION = "awaiting-verification"
    COMPLETE = "complete"
