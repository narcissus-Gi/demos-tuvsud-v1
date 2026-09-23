# 根据配置创建检查点
# 只负责创建 checkpointer，不负责具体图的节点和边。


from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver


def create_checkpointer() -> InMemorySaver:

    return InMemorySaver()