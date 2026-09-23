# 定义文档片段结构

from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from common.contracts import (
    Evidence,
    EvidenceSourceType,
)


class DocumentChunk(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    doc_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    section: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)

    content: str = Field(min_length=1)

    # 用于过滤不同设备型号的资料。
    device_model: str | None = None

    # 空集合表示公共资料；非空表示仅允许指定产线访问。
    allowed_lines: frozenset[str] = Field(
        default_factory=frozenset
    )

    @field_validator(
        "doc_id",
        "version",
        "section",
        "chunk_id",
        "content",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("value cannot be empty")

        return normalized

    @field_validator("device_model")
    @classmethod
    def normalize_device_model(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper()

        return normalized or None

    @field_validator("allowed_lines", mode="before")
    @classmethod
    def normalize_allowed_lines(
        cls,
        value: object,
    ) -> frozenset[str]:
        if value is None:
            return frozenset()

        if isinstance(value, str):
            value = [value]

        return frozenset(
            str(line_id).strip().upper()
            for line_id in value
            if str(line_id).strip()
        )

    @property
    def evidence_id(self) -> str:
        """生成稳定、可读的引用编号。"""

        return (
            f"{self.doc_id}/"
            f"{self.version}/"
            f"{self.section}/"
            f"{self.chunk_id}"
        )

    def to_evidence(self) -> Evidence:

        return Evidence(
            evidence_id=self.evidence_id,
            source_type=EvidenceSourceType.DOCUMENT,
            source_id=self.doc_id,
            content=self.content,
            metadata={
                "doc_id": self.doc_id,
                "version": self.version,
                "section": self.section,
                "chunk_id": self.chunk_id,
                "device_model": self.device_model,
                "allowed_lines": sorted(
                    self.allowed_lines
                ),
            },
        )