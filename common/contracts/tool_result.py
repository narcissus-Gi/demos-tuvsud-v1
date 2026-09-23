# 定义统一工具返回结构

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .errors import ErrorInfo


DataT = TypeVar("DataT")


class ToolResult(BaseModel, Generic[DataT]):

    model_config = ConfigDict(extra="forbid")

    ok: bool
    data: DataT | None = None
    error: ErrorInfo | None = None

    source_ids: list[str] = Field(default_factory=list)
    observed_at: datetime | None = None

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("observed_at must include timezone")
        return value

    @model_validator(mode="after")
    def validate_result_consistency(self) -> "ToolResult[DataT]":
        if self.ok and self.error is not None:
            raise ValueError(
                "successful tool result cannot contain an error"
            )

        if not self.ok and self.error is None:
            raise ValueError(
                "failed tool result must contain an error"
            )

        if not self.ok and self.data is not None:
            raise ValueError(
                "failed tool result cannot contain data"
            )

        return self

    @classmethod
    def success(
        cls,
        data: DataT | None = None,
        *,
        source_ids: list[str] | None = None,
        observed_at: datetime | None = None,
    ) -> "ToolResult[DataT]":
        return cls(
            ok=True,
            data=data,
            error=None,
            source_ids=source_ids or [],
            observed_at=observed_at,
        )

    @classmethod
    def failure(
        cls,
        error: ErrorInfo,
        *,
        observed_at: datetime | None = None,
    ) -> "ToolResult[DataT]":
        return cls(
            ok=False,
            data=None,
            error=error,
            source_ids=[],
            observed_at=observed_at,
        )