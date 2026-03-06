# Aigen Python AI Service

> 🤖 LangGraph 驱动的智能代码生成 Agent 工作流服务

本模块是 Aigen 平台的 AI 算法端，通过 **LangChain + LangGraph** 编排 7 节点 StateGraph 工作流，完成从用户需求到代码生成的全流程，并将执行进度通过 **SSE 流式**推送给 Java 主服务。

## 技术栈

| 组件 | 版本 | 用途 |
|---|---|---|
| Python | 3.12 | 运行时 |
| FastAPI | 0.115+ | 异步 Web 框架 |
| LangGraph | 0.2+ | StateGraph 工作流编排 |
| LangChain | 0.3+ | LLM 调用 / Tool Calling |
| DashScope (Qwen) | OpenAI 兼容 | 大语言模型 |
| Redis | 7 | 与 Java 端共享 Session |

## 快速开始

### 1. 创建虚拟环境

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

### 3. 配置环境变量

```bash
copy .env.example .env
# 必须填写: DASHSCOPE_API_KEY
# 可选填写: PEXELS_API_KEY, JAVA_CORE_INTERNAL_SECRET
```

### 4. 启动开发服务器

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

### 5. 查看 API 文档

访问 http://localhost:8100/docs

## 项目结构

```
aigen-python-ai/
├── app/
│   ├── main.py                  # FastAPI 入口 & 路由注册
│   ├── config.py                # Pydantic Settings 配置管理
│   ├── api/
│   │   ├── deps.py              # 服务间 Token 校验
│   │   └── endpoints/
│   │       ├── health.py        # 健康检查
│   │       ├── workflow.py      # SSE 代码生成工作流接口 ⭐
│   │       └── chat.py          # LLM 对话测试接口
│   ├── graph/
│   │   ├── state.py             # AgentState (TypedDict)
│   │   ├── workflow.py          # StateGraph 图编排 & 条件路由
│   │   └── nodes/               # 7 个工作流节点
│   │       ├── image_collector.py    # 并发图片/素材收集
│   │       ├── prompt_enhancer.py    # 提示词增强 + 图片注入
│   │       ├── router.py             # LLM 智能路由
│   │       ├── knowledge_retrieval.py# RAG 知识检索
│   │       ├── code_generator.py     # 代码生成 (Tool Calling)
│   │       ├── quality_check.py      # LLM 代码质量审查
│   │       └── project_builder.py    # npm 构建 (Vue)
│   ├── tools/
│   │   ├── file_tools.py        # 文件操作工具 (沙箱 by app_id)
│   │   └── image_tools.py       # 图片/素材工具 (Pexels/Undraw/DashScope)
│   ├── services/
│   │   ├── llm_service.py       # LLM 工厂 (通用/推理/代码生成)
│   │   ├── code_generator.py    # 代码解析 & 磁盘保存
│   │   └── rag_service.py       # RAG 知识库检索
│   └── models/
│       ├── schemas.py           # 请求/响应 Pydantic 模型
│       └── enums.py             # CodeGenType 等枚举
├── pyproject.toml               # 依赖管理
├── .env.example                 # 环境变量模板
└── Dockerfile                   # 多阶段构建
```

## 与 Java 主服务的协作

```
Java 端: PythonAiServiceClient.streamWorkflow()
  │  HTTP GET /api/v1/ai/workflow/generate?task_id=...&prompt=...
  │
  ▼
Python 端: GET /api/v1/ai/workflow/generate
  │  执行 LangGraph StateGraph
  │
  ▼  SSE 事件流 (text/event-stream)
  ├── event: workflow_start      → 工作流启动
  ├── event: step_start          → 节点开始
  ├── event: code_chunk          → LLM 流式 token
  ├── event: step_completed      → 节点完成
  └── event: workflow_completed  → 全部完成
```

## 新增节点指南

```python
# 1. 在 app/graph/nodes/ 新建文件
async def your_node(state: AgentState) -> dict:
    # 处理逻辑...
    return {"current_step": "your_node", "your_field": result}

# 2. 在 workflow.py 注册
graph.add_node("your_node", your_node)
graph.add_edge("previous_node", "your_node")

# 3. 在 workflow.py endpoint 添加中文标签
_step_labels = { "your_node": "你的节点名称" }
```
