from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessException
from app.config import settings
from app.models.user import User
from app.schemas.ai import ChatRequest
from app.services import agent_tools


SYSTEM_PROMPT = """你是智能实验室预约系统的 Agent，回答要简洁。
你可以：
1. 使用 search_lab_docs 查询实验室的规则、安全、开放时间等问题
2. 使用 list_open_labs / list_lab_equipments 查询真实的实验室和设备
3. 在用户进行了预约确认后，使用 create_lab_reservation 进行真实的预约落库
4. 使用 get_today 进行日期换算

## 必须遵守
当用户提到了今天、明天、后天等日期相关的问题，请先调用 get_today 获取日期。

提交预约之前必须向用户复述：实验室 ID 与名称（或设备 ID 和名称）、日期、开始时间、结束时间，并得到用户确认再进行实际操作。
用户没说【确认】【确认预约】【就这样预约】等确定性回复之前，不要调用 create_lab_reservation。
确认环节如果缺少 lab_id，请先用 list_open_labs 查询，不要编造。
确认环节如果缺少 equipment_id，请先用 list_lab_equipments 查询，不要编造。

预约成功后状态是待审核，必须管理员审核通过后才能使用。
不要编造数据库里没有的实验室或设备信息。
如果询问具体实验室的开放时间，调用 list_open_labs 查询当前数据；询问预约规则时调用 search_lab_docs。
"""

TOOL_LABELS = {
    "search_lab_docs": "检索实验室知识库",
    "list_open_labs": "查询开放实验室",
    "list_lab_equipments": "查询实验室设备",
    "create_lab_reservation": "提交预约",
    "get_today": "获取今天日期",
}


def build_agent(db: Session, current_user: User):
    tools = agent_tools.build_tools(db, current_user)
    llm = ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=0,
        streaming=True,
    ).bind_tools(tools)

    async def agent_node(state: MessagesState, config: RunnableConfig):
        response = await llm.ainvoke(state["messages"], config=config)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


def _chunk_text(chunk: Any) -> str:
    """将模型流式消息的内容转成纯文本。"""
    if chunk is None:
        return ""
    content = getattr(chunk, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text") or "")
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return str(content) if content is not None else ""


def _tool_output_preview(output: Any, limit: int = 200) -> str:
    """截取工具结果供前端展示。"""
    if isinstance(output, ToolMessage):
        output = output.content
    text = output if isinstance(output, str) else str(output)
    return text if len(text) <= limit else text[:limit] + "…"


def _build_history(data: ChatRequest) -> list:
    """只把对话文本转成 LangChain 消息。"""
    history = []
    for message in data.messages or []:
        if message.role == "user" and message.content.strip():
            history.append(HumanMessage(content=message.content.strip()))
        elif message.role == "assistant" and message.content.strip():
            history.append(AIMessage(content=message.content.strip()))
    if not history:
        raise BusinessException(message="请输入您要对话的内容")
    return history


async def stream_agent(db: Session, current_user: User, data: ChatRequest) -> AsyncIterator[dict]:
    """逐条生成状态、工具过程和回答文本，供 SSE 接口发送。"""
    try:
        history = _build_history(data)
        if not settings.LLM_API_KEY:
            raise BusinessException(message="未获取到大模型的API Key")
        agent = build_agent(db, current_user)
        inputs = {"messages": [SystemMessage(content=SYSTEM_PROMPT), *history]}
        yield {"type": "status", "message": "正在思考…"}

        async for event in agent.astream_events(
            inputs,
            version="v2",
            config={"recursion_limit": 10},
        ):
            kind = event.get("event")
            if kind == "on_tool_start":
                name = event.get("name") or ""
                yield {"type": "tool_start", "name": name, "label": TOOL_LABELS.get(name, name)}
            elif kind == "on_tool_end":
                name = event.get("name") or ""
                yield {
                    "type": "tool_end",
                    "name": name,
                    "label": TOOL_LABELS.get(name, name),
                    "preview": _tool_output_preview((event.get("data") or {}).get("output")),
                }
            elif kind == "on_chat_model_stream":
                meta = event.get("metadata") or {}
                if meta.get("langgraph_node") not in (None, "agent"):
                    continue
                text = _chunk_text((event.get("data") or {}).get("chunk"))
                if text:
                    yield {"type": "token", "content": text}

        yield {"type": "done"}
    except BusinessException as exc:
        yield {"type": "error", "message": exc.message}
    except Exception:
        yield {"type": "error", "message": "大模型调用失败，请稍后重试"}
