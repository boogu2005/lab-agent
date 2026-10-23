from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"comment": "AI 对话消息"}

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, comment="用户ID", nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(16), comment="角色：user-用户，assistant-助手", nullable=False
    )
    content: Mapped[str] = mapped_column(Text, comment="消息内容", nullable=False)
