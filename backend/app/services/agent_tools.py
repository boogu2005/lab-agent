from datetime import datetime
import json

from langchain_core.tools import tool
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.database import SessionLocal
from app.models.user import User
from app.schemas.reservation import ReservationCreateRequest
from app.services import equipment_service, kb_service, lab_service, reservation_service


def build_tools(user_id: int):
    """构造工具集。

    LangGraph 的 ToolNode 会并发执行同一轮里的多个 tool call，
    每个工具必须使用自己的 Session，不能共用请求级的会话。
    """

    def load_user(db: Session) -> User:
        user = db.get(User, user_id)
        if user is None or user.status != 1:
            raise BusinessException(message="用户不存在或已被禁用，请重新登录")
        return user

    @tool
    def search_lab_docs(query: str) -> str:
        """根据用户的提问检索知识库。"""
        try:
            return kb_service.search(query) or "没有检索到相关的资料"
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def list_open_labs(keywords: str = "") -> str:
        """查询开放的实验室列表。"""
        try:
            with SessionLocal() as db:
                page = lab_service.get_lab_page_list(
                    db, page=1, page_size=20, keywords=keywords.strip() or None, status=1
                )
                rows = [
                    {
                        "id": item.id,
                        "name": item.name,
                        "location": item.location,
                        "capacity": item.capacity,
                        "open_time": item.open_time,
                        "close_time": item.close_time,
                    }
                    for item in page.list
                ]
            return json.dumps({"total": page.total, "labs": rows}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def list_lab_equipments(lab_id: int, keywords: str = "") -> str:
        """查询某个实验室可用的设备列表。"""
        try:
            with SessionLocal() as db:
                page = equipment_service.get_equipment_page_list(
                    db, page=1, page_size=10, lab_id=lab_id, keywords=keywords.strip() or None
                )
                rows = [
                    {
                        "id": item.id,
                        "name": item.name,
                        "lab_id": item.lab_id,
                        "lab_name": item.lab_name,
                        "spec": item.spec,
                        "quantity": item.quantity,
                        "status": item.status,
                    }
                    for item in page.list
                    if item.status == 1
                ]
            return json.dumps({"total": len(rows), "equipments": rows}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def create_lab_reservation(
        lab_id: int,
        date: str,
        start_time: str,
        end_time: str,
        equipment_id: int | None = None,
        remark: str | None = None,
    ) -> str:
        """创建预约单，预约实验室或设备。"""
        try:
            with SessionLocal() as db:
                user = load_user(db)
                data = ReservationCreateRequest(
                    lab_id=lab_id,
                    equipment_id=equipment_id,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    remark=remark,
                )
                reservation_service.create_reservation(db, user, data)
            return json.dumps(
                {
                    "ok": True,
                    "message": "预约已提交，请等待管理员审核",
                    "lab_id": lab_id,
                    "equipment_id": equipment_id,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                },
                ensure_ascii=False,
            )
        except ValidationError:
            return json.dumps({"ok": False, "error": "预约日期或时间格式错误"}, ensure_ascii=False)
        except BusinessException as exc:
            return json.dumps({"ok": False, "error": exc.message}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def get_today() -> str:
        """获取服务器当前日期。"""
        return datetime.now().strftime("%Y-%m-%d")

    return [
        search_lab_docs,
        list_open_labs,
        list_lab_equipments,
        create_lab_reservation,
        get_today,
    ]
