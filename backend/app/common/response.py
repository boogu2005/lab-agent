from typing import Any
from pydantic import BaseModel


class Response(BaseModel):
    """统一响应模型，包含状态码、消息和数据，用于封装API的返回结果"""

    code: int
    message: str
    data: Any = {}


@classmethod
def success(cls, message: str = "请求成功", data: Any = None):
    return cls(code=200, message=message, data=data)


@classmethod
def error(cls, message: str = "请求失败", data: Any = None):
    return cls(code=400, message=message, data=data)
