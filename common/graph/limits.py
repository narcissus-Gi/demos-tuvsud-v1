# 负责业务执行上限

from __future__ import annotations

from enum import StrEnum
from typing import Any, Mapping

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class LimitReason(StrEnum):
    MODEL_CALL_LIMIT = "model_call_limit"
    TOOL_ATTEMPT_LIMIT = "tool_attempt_limit"
    EXECUTION_TIME_LIMIT = "execution_time_limit"


class ExecutionLimits(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    max_model_calls: int = Field(
        default=6,
        ge=1,
    )
    max_tool_attempts: int = Field(
        default=6,
        ge=1,
    )
    max_execution_seconds: float = Field(
        default=60,
        gt=0,
    )


class LimitCheck(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    allowed: bool
    reason: LimitReason | None = None


def check_execution_limits(
    state: Mapping[str, Any],
    limits: ExecutionLimits,
    *,
    elapsed_seconds: float,
) -> LimitCheck:

    model_calls = int(
        state.get("model_calls", 0)
    )
    tool_attempts = int(
        state.get("tool_attempts", 0)
    )

    if model_calls >= limits.max_model_calls:
        return LimitCheck(
            allowed=False,
            reason=LimitReason.MODEL_CALL_LIMIT,
        )

    if tool_attempts >= limits.max_tool_attempts:
        return LimitCheck(
            allowed=False,
            reason=LimitReason.TOOL_ATTEMPT_LIMIT,
        )

    if elapsed_seconds >= limits.max_execution_seconds:
        return LimitCheck(
            allowed=False,
            reason=LimitReason.EXECUTION_TIME_LIMIT,
        )

    return LimitCheck(allowed=True)