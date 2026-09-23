# 负责程序化检查：
# - 引用是否存在
# - 引用是否属于本次检索结果
# - 引用是否符合型号和版本
# - 引用是否属于用户授权范围
# - 是否引用了不存在的 chunk_id


from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from common.contracts import (
    Citation,
    Evidence,
)
from common.security import RequestContext


class CitationValidationResult(BaseModel):
    """引用校验结果。"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    valid: bool

    accepted: list[Citation] = Field(
        default_factory=list
    )
    invalid_ids: list[str] = Field(
        default_factory=list
    )
    reasons: dict[str, str] = Field(
        default_factory=dict
    )


def validate_citations(
    *,
    citations: list[Citation],
    available_evidence: list[Evidence],
    context: RequestContext,
    expected_device_model: str | None = None,
    expected_version: str | None = None,
    require_at_least_one: bool = True,
) -> CitationValidationResult:
    """验证引用是否属于本次授权检索结果。"""

    evidence_by_id = {
        item.evidence_id: item
        for item in available_evidence
    }

    accepted: list[Citation] = []
    invalid_ids: list[str] = []
    reasons: dict[str, str] = {}
    seen_ids: set[str] = set()

    normalized_model = (
        expected_device_model.strip().upper()
        if expected_device_model
        else None
    )

    for citation in citations:
        evidence_id = citation.evidence_id

        if evidence_id in seen_ids:
            continue

        seen_ids.add(evidence_id)

        evidence = evidence_by_id.get(evidence_id)

        if evidence is None:
            invalid_ids.append(evidence_id)
            reasons[evidence_id] = (
                "not_in_retrieved_evidence"
            )
            continue

        metadata = evidence.metadata

        allowed_lines = {
            str(line_id).strip().upper()
            for line_id in metadata.get(
                "allowed_lines",
                [],
            )
        }

        if (
            allowed_lines
            and not (
                allowed_lines
                & context.allowed_lines
            )
        ):
            invalid_ids.append(evidence_id)
            reasons[evidence_id] = (
                "forbidden_scope"
            )
            continue

        evidence_model = metadata.get(
            "device_model"
        )

        if (
            normalized_model
            and evidence_model
            and str(evidence_model).upper()
            != normalized_model
        ):
            invalid_ids.append(evidence_id)
            reasons[evidence_id] = (
                "device_model_mismatch"
            )
            continue

        evidence_version = metadata.get(
            "version"
        )

        if (
            expected_version
            and evidence_version
            != expected_version
        ):
            invalid_ids.append(evidence_id)
            reasons[evidence_id] = (
                "document_version_mismatch"
            )
            continue

        accepted.append(citation)

    if require_at_least_one and not accepted:
        return CitationValidationResult(
            valid=False,
            accepted=[],
            invalid_ids=invalid_ids,
            reasons={
                **reasons,
                "_result": "no_valid_citation",
            },
        )

    return CitationValidationResult(
        valid=not invalid_ids,
        accepted=accepted,
        invalid_ids=invalid_ids,
        reasons=reasons,
    )