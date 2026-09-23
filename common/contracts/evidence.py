# 定义所有 Agent 都可使用的证据结构
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class EvidenceSourceType(StrEnum):
    DOCUMENT = "document"
    DATABASE = "database"
    TOOL = "tool"
    DEVICE_SNAPSHOT = "device_snapshot"
    HISTORICAL_CASE = "historical_case"
    USER_INPUT = "user_input"


class Evidence(BaseModel):

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    source_type: EvidenceSourceType
    source_id: str = Field(min_length=1)

    content: str = Field(min_length=1)

    observed_at: datetime | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(
        cls,
        value: datetime | None,
    ):
        if value is not None and value.tzinfo is None:
            raise ValueError("observed_at must include timezone")
        return value


class Citation(BaseModel):

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)

    claim: str | None = None

    locator: str | None = None