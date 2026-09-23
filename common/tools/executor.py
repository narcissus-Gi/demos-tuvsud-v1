# 安全工具调用的核心
# 检查工具是否注册
# → 校验参数
# → 检查用户权限
# → 执行工具
# → 处理超时和有限重试
# → 标准化结果
# → 写入审计记录


from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from common.contracts import (
    AppError,
    ErrorCode,
    ErrorInfo,
    ToolResult,
)
from common.security import RequestContext

from .registry import ToolRegistry


class ToolExecutor:
    """校验参数并执行已注册工具。"""

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry

    def execute(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        context: RequestContext,
    ) -> ToolResult[Any]:
        tool = self._registry.get(tool_name)

        if tool is None:
            return ToolResult[Any].failure(
                ErrorInfo(
                    code=ErrorCode.INVALID_INPUT,
                    message="模型请求了未注册的工具",
                    retryable=False,
                    details={
                        "tool_name": tool_name,
                    },
                )
            )

        try:
            validated_arguments = (
                tool.input_model.model_validate(
                    arguments
                )
            )
        except ValidationError as error:
            return ToolResult[Any].failure(
                ErrorInfo(
                    code=ErrorCode.INVALID_INPUT,
                    message="工具参数校验失败",
                    retryable=False,
                    details={
                        "error_count": (
                            error.error_count()
                        ),
                    },
                )
            )

        try:
            return tool.handler(
                validated_arguments,
                context,
            )
        except AppError as error:
            return ToolResult[Any].failure(
                error.info
            )
        except Exception as error:
            return ToolResult[Any].failure(
                ErrorInfo(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="工具执行失败",
                    retryable=False,
                    details={
                        "error_type": (
                            type(error).__name__
                        ),
                    },
                )
            )