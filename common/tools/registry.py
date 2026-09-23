from __future__ import annotations

from typing import Any

from .base import DemoTool


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, DemoTool] = {}

    def register(self, tool: DemoTool) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"duplicate tool name: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> DemoTool | None:
        return self._tools.get(name)

    def model_schemas(self) -> list[dict[str, Any]]:
        return [
            tool.model_schema()
            for tool in self._tools.values()
        ]