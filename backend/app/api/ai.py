import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest
from app.services import agent_service


router = APIRouter(prefix="/ai", tags=["AI相关的API"])


def _sse_line(payload: dict) -> str:
    """以空行结束一条 SSE 帧。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id

    async def event_gen():
        # 只在这里校验一次用户；工具执行时会各自打开独立会话。
        with SessionLocal() as db:
            stream_user = db.get(User, user_id)
            if stream_user is None or stream_user.status != 1:
                yield _sse_line({"type": "error", "message": "用户不存在或已被禁用，请重新登录"})
                return
        async for event in agent_service.stream_agent(user_id, data):
            yield _sse_line(event)

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
