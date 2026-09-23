# 定义统一模型接口

from __future__ import annotations

from typing import TypeAlias

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


ChatModel: TypeAlias = BaseChatModel


class ModelCreationError(RuntimeError):
    """模型客户端无法创建时抛出的统一异常。"""


def extract_message_text(message: BaseMessage) -> str:

    content = message.content

    if isinstance(content, str):
        return content

    texts: list[str] = []

    for block in content:
        if isinstance(block, str):
            texts.append(block)
            continue

        if isinstance(block, dict):
            text = block.get("text")

            if isinstance(text, str):
                texts.append(text)

    return "\n".join(texts)