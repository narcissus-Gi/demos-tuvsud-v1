# 定义检索接口


from __future__ import annotations

import re
from typing import Protocol

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from common.security import RequestContext

from .document import DocumentChunk


ASCII_TOKEN_PATTERN = re.compile(
    r"[a-zA-Z0-9_-]+"
)
CHINESE_SEQUENCE_PATTERN = re.compile(
    r"[\u4e00-\u9fff]+"
)


def tokenize(text: str) -> set[str]:
    """课堂 Demo 使用的极简关键词切分。"""

    normalized = text.lower()
    tokens = set(
        ASCII_TOKEN_PATTERN.findall(normalized)
    )

    for sequence in CHINESE_SEQUENCE_PATTERN.findall(
        normalized
    ):
        if len(sequence) <= 2:
            tokens.add(sequence)
            continue

        for index in range(len(sequence) - 1):
            tokens.add(
                sequence[index:index + 2]
            )

    return tokens


class RetrievalHit(BaseModel):
    """一条检索命中。"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    chunk: DocumentChunk
    score: int = Field(ge=1)


class Retriever(Protocol):
    """以后替换向量库时保持相同接口。"""

    def search(
        self,
        query: str,
        *,
        context: RequestContext,
        top_k: int = 3,
        device_model: str | None = None,
        document_version: str | None = None,
    ) -> list[RetrievalHit]:
        ...


class InMemoryKeywordRetriever:
    """课堂 Demo 使用的内存关键词检索器。"""

    def __init__(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        self._chunks = list(chunks)

    def search(
        self,
        query: str,
        *,
        context: RequestContext,
        top_k: int = 3,
        device_model: str | None = None,
        document_version: str | None = None,
    ) -> list[RetrievalHit]:
        if not 1 <= top_k <= 5:
            raise ValueError(
                "top_k must be between 1 and 5"
            )

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        normalized_model = (
            device_model.strip().upper()
            if device_model
            else None
        )

        hits: list[RetrievalHit] = []

        for chunk in self._chunks:
            if not self._is_authorized(
                chunk,
                context,
            ):
                continue

            if (
                normalized_model
                and chunk.device_model
                != normalized_model
            ):
                continue

            if (
                document_version
                and chunk.version
                != document_version
            ):
                continue

            searchable_text = " ".join(
                [
                    chunk.doc_id,
                    chunk.version,
                    chunk.section,
                    chunk.chunk_id,
                    chunk.device_model or "",
                    chunk.content,
                ]
            )

            document_tokens = tokenize(
                searchable_text
            )
            score = len(
                query_tokens & document_tokens
            )

            if score == 0:
                continue

            hits.append(
                RetrievalHit(
                    chunk=chunk,
                    score=score,
                )
            )

        hits.sort(
            key=lambda hit: (
                -hit.score,
                hit.chunk.evidence_id,
            )
        )

        return hits[:top_k]

    @staticmethod
    def _is_authorized(
        chunk: DocumentChunk,
        context: RequestContext,
    ) -> bool:
        # 没有设置产线范围的文档视为公共文档。
        if not chunk.allowed_lines:
            return True

        return bool(
            chunk.allowed_lines
            & context.allowed_lines
        )