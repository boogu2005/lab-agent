from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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
如果询问开放时间或实验室规则，优先调用 search_lab_docs。
"""


def build_agent(db: Session, current_user: User):
    tools = agent_tools.build_tools(db, current_user)
    llm = ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=0,
    ).bind_tools(tools)

    def agent_node(state: MessagesState):
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


def run_agent(db: Session, current_user: User, data: ChatRequest):
    """运行 LangGraph 对话工作流。"""
    if not data.messages:
        raise BusinessException(message="对话内容为空")
    history = []
    for message in data.messages:
        if message.role == "user" and message.content.strip():
            history.append(HumanMessage(content=message.content.strip()))
        elif message.role == "assistant" and message.content.strip():
            history.append(AIMessage(content=message.content.strip()))
    if not history:
        raise BusinessException(message="请输入您要对话的内容")
    if not settings.LLM_API_KEY:
        raise BusinessException(message="未获取到大模型的API Key")

    agent = build_agent(db, current_user)
    try:
        result = agent.invoke(
            {"messages": [SystemMessage(content=SYSTEM_PROMPT), *history]},
            config={"recursion_limit": 10},
        )
    except BusinessException:
        raise
    except Exception as exc:
        raise BusinessException(message="大模型调用失败，请稍后重试") from exc

    messages = result.get("messages") or []
    if not messages:
        raise BusinessException(message="大模型没有任何返回内容")
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            content = message.content
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            if isinstance(content, str) and content.strip():
                return content.strip()
    raise BusinessException(message="大模型没有返回可用内容")
