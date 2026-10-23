import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.common.response import Response
from app.database import SessionLocal, get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest
from app.services import agent_service, chat_history_service


router = APIRouter(prefix="/ai", tags=["AI相关的API"])


def _sse_line(payload: dict) -> str:
    """以空行结束一条 SSE 帧。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.get("/chat/history")
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = chat_history_service.list_messages(db, current_user.id)
    return Response.success(
        data=[{"role": row.role, "content": row.content} for row in rows]
    )


@router.delete("/chat/history")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_history_service.clear_messages(db, current_user.id)
    return Response.success(message="对话已清空")


@router.post("/chat/stream")
async def chat_stream(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    # 前端只需传新提问；历史以数据库为准
    question = next(
        (
            message.content.strip()
            for message in reversed(data.messages)
            if message.role == "user" and message.content.strip()
        ),
        "",
    )

    async def event_gen():
        # 只在这里校验一次用户；工具执行时会各自打开独立会话。
        with SessionLocal() as db:
            stream_user = db.get(User, user_id)
            if stream_user is None or stream_user.status != 1:
                yield _sse_line({"type": "error", "message": "用户不存在或已被禁用，请重新登录"})
                return
            if not question:
                yield _sse_line({"type": "error", "message": "请输入您要对话的内容"})
                return
            # 先落库用户提问，再连同历史一起送进 Agent
            chat_history_service.append_message(db, user_id, "user", question)
        async for event in agent_service.stream_agent(user_id):
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
