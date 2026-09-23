# 负责统一构建 LangGraph 运行配置


from __future__ import annotations

from typing import Any
from uuid import uuid4

from langchain_core.runnables import RunnableConfig


def new_request_id() -> str:
    """生成一次业务请求的唯一编号。"""

    return f"REQ-{uuid4()}"


def new_thread_id() -> str:
    """生成一次 LangGraph 会话编号。"""

    return f"THREAD-{uuid4()}"


def build_run_config(
    *,
    thread_id: str,
    recursion_limit: int = 50,
    configurable: dict[str, Any] | None = None,
) -> RunnableConfig:
    """创建 graph.invoke/stream 使用的运行配置。"""

    normalized_thread_id = thread_id.strip()

    if not normalized_thread_id:
        raise ValueError(
            "thread_id cannot be empty"
        )

    if len(normalized_thread_id) > 255:
        raise ValueError(
            "thread_id cannot exceed 255 characters"
        )

    if recursion_limit < 1:
        raise ValueError(
            "recursion_limit must be greater than zero"
        )

    extra_config = dict(configurable or {})

    if "thread_id" in extra_config:
        raise ValueError(
            "thread_id must be provided separately"
        )

    return {
        "configurable": {
            "thread_id": normalized_thread_id,
            **extra_config,
        },
        "recursion_limit": recursion_limit,
    }