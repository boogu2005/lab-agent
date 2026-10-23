from sqlalchemy.orm import Session

from app.models.chat import ChatMessage

# 送入大模型上下文的最多消息条数，避免历史无限增长
MAX_HISTORY = 40


def list_messages(db: Session, user_id: int, limit: int | None = None) -> list[ChatMessage]:
    """按时间正序返回某个用户的对话记录。"""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if limit:
        rows = query.order_by(ChatMessage.id.desc()).limit(limit).all()
        rows.reverse()
        return rows
    return query.order_by(ChatMessage.id.asc()).all()


def append_message(db: Session, user_id: int, role: str, content: str) -> ChatMessage:
    message = ChatMessage(user_id=user_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def clear_messages(db: Session, user_id: int) -> int:
    count = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
    return count
