# 记录一次 LangGraph 执行轨迹
# 
# 主要用于：
# - 解释流程为什么进入某条分支
# - 定位工具或模型失败
# - 统计模型调用和工具尝试次数
# - 展示达到上限后为何停止
# 不需要记录模型的隐藏思维过程。


from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Protocol
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from common.contracts import AppError, ErrorCode


# Trace 只允许记录简单摘要，不接受任意复杂对象。
TraceValue = str | int | float | bool | None


class TraceStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TraceEvent(BaseModel):
    """一条 LangGraph 节点运行轨迹。"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    event_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    request_id: str
    node_name: str
    status: TraceStatus

    duration_ms: float | None = Field(
        default=None,
        ge=0,
    )

    input_summary: dict[str, TraceValue] = Field(
        default_factory=dict
    )
    output_summary: dict[str, TraceValue] = Field(
        default_factory=dict
    )

    model_calls: int | None = Field(
        default=None,
        ge=0,
    )
    tool_attempts: int | None = Field(
        default=None,
        ge=0,
    )

    error_code: ErrorCode | None = None
    error_type: str | None = None


class TraceRecorder(Protocol):
    """轨迹记录器统一接口。"""

    def record(self, event: TraceEvent) -> None:
        ...


class NoOpTraceRecorder:
    """关闭 Trace 时使用，不执行任何操作。"""

    def record(self, event: TraceEvent) -> None:
        del event


class InMemoryTraceRecorder:
    """单元测试使用的内存轨迹记录器。"""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def record(self, event: TraceEvent) -> None:
        self.events.append(event)


class JsonlTraceRecorder:
    """将运行轨迹保存为 JSON Lines 文件。"""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()

    def record(self, event: TraceEvent) -> None:
        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        line = event.model_dump_json()

        with self._lock:
            with self._path.open(
                mode="a",
                encoding="utf-8",
            ) as file:
                file.write(line)
                file.write("\n")