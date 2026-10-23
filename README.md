# 实验室智能预约系统

一个基于 FastAPI 和 Vue 3 的实验室预约课程项目。系统提供实验室与设备管理、预约和审核，并接入 AI 助手查询开放实验室、检索规则和辅助预约。

## 功能

- 用户注册、登录与资料管理；管理员可管理用户、实验室和设备。
- 用户查看实验室与设备，提交或取消预约；管理员审核预约。
- AI 助手通过 LangGraph 调用实验室查询、知识库检索和预约工具，以 SSE 流式返回结果。
- 聊天记录按用户保存，支持查看和清空。

## 技术栈

| 部分 | 技术 |
| --- | --- |
| 后端 | Python、FastAPI、SQLAlchemy、MySQL、JWT |
| 前端 | Vue 3、Vite、Element Plus、Axios |
| AI 助手 | LangGraph、LangChain 的模型与工具组件 |
| 知识库 | ChromaDB、Sentence Transformers（`BAAI/bge-small-zh-v1.5`） |

## 项目结构

```text
backend/
  app/api/          # 接口
  app/models/       # 数据表模型
  app/services/     # 业务逻辑、Agent 与知识库
  data/kb/          # 知识库 Markdown 资料
  requirements.txt
frontend/
  src/views/        # 页面
  src/api/          # 前端接口调用
  package.json
LICENSE
```

## 本地运行

需要 MySQL、Python 3.10 和符合 `frontend/package.json` 要求的 Node.js（`^22.18.0` 或 `>=24.12.0`）。先在 MySQL 中创建一个空数据库，例如：

```sql
CREATE DATABASE lab_agent DEFAULT CHARACTER SET utf8mb4;
```

首次获取项目时，在 PowerShell 中克隆仓库，并进入项目根目录：

```powershell
git clone https://github.com/boogu2005/lab-agent.git
cd .\lab-agent
```

### 1. 启动后端

从项目根目录进入后端目录，创建虚拟环境并安装依赖：

```powershell
cd .\backend
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

在 `backend/.env` 中填写自己的配置：

```dotenv
DATABASE_URL=mysql+pymysql://db_user:db_password@127.0.0.1:3306/lab_agent?charset=utf8mb4
JWT_SECRET_KEY=replace_with_a_long_random_string
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://your-openai-compatible-api.example/v1
LLM_MODEL=your_tool_calling_model
```

`DATABASE_URL` 和 `JWT_SECRET_KEY` 为必填项。AI 助手还需要支持工具调用和流式输出的模型接口。`.env` 已被 Git 忽略，请勿提交真实密钥。

仍在 `backend` 目录下启动服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app
```

后端接口文档：<http://127.0.0.1:8000/docs>。首次使用知识库时，程序可能需要下载 `BAAI/bge-small-zh-v1.5` 模型。后端启动时会根据 SQLAlchemy 模型创建尚不存在的表。

### 2. 启动前端

另开一个 PowerShell 终端，在项目根目录执行：

```powershell
cd .\frontend
npm ci
npm run dev
```

打开 <http://localhost:5173/>。开发服务器会把 `/api` 和 `/uploads` 请求转发到 `http://127.0.0.1:8000`。

## 许可证

本项目采用 [MIT License](LICENSE)。
