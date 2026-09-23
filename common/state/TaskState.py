# 定义了所有agent都可用的公共状态
# 根据demo具体需要 在个人文件夹中增加相关字段

from typing import Any
from typing_extensions import TypedDict

class BaseTaskState(TypedDict, total=False):
    request_id: str
    user_query: str
    intent: str
    line_id: str
    device_id: str
    start_time: str
    end_time: str
    evidence: list[dict]
    metrics: dict
    result: dict
    status: str
    missing_fields: list[str]
    tool_attempts: int
    model_calls: int
    errors: list[dict]
    draft_id: str
    payload_hash: str