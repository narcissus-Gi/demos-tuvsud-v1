from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from common.contracts import ToolResult
from common.security import RequestContext


ToolHandler = Callable[
    [BaseModel, RequestContext],
    ToolResult[Any],
]


@dataclass(frozen=True)
class DemoTool:

    name: str
    description: str
    input_model: type[BaseModel]
    handler: ToolHandler

    def model_schema(self) -> dict[str, Any]:
        """生成模型 Tool Calling 使用的 Schema。"""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": (
                    self.input_model.model_json_schema()
                ),
            },
        }