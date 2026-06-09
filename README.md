# AI 工程化实验室

一个用于学习和实践 AI 工程化技术的交互式项目。按照 **Prompt -> RAG -> Agent -> 完整项目** 的路线，帮助你系统掌握大模型应用开发的核心技能。

## 项目结构

```
ai-engineering-lab/
├── prompts/              # Prompt 工程模块
│   ├── basics.py         # 基础 Prompt 技巧（角色设定、指令、上下文等）
│   ├── advanced.py       # 进阶 Prompt 技巧（Few-shot、CoT、ToT、ReAct 等）
│   ├── debug_tools.py    # Prompt 调试与评估工具
│   └── templates/        # 可复用的 Prompt 模板库
├── rag/                  # RAG（检索增强生成）模块
│   ├── document_loader.py    # 文档加载与分块
│   ├── embedding.py          # 文本向量化
│   ├── vector_store.py       # 向量数据库存储
│   ├── retriever.py          # 相似度检索与重排序
│   ├── generator.py          # 基于上下文的答案生成
│   └── pipeline.py           # 完整 RAG Pipeline
├── agent/                # Agent（智能体）模块
│   ├── tools/            # 工具定义
│   │   ├── search_tool.py
│   │   ├── calculator_tool.py
│   │   └── weather_tool.py
│   ├── planner.py        # 任务规划器
│   ├── executor.py       # 工具执行器
│   ├── memory.py         # 对话记忆管理
│   └── agent_core.py     # ReAct 风格 Agent 核心
├── integration/          # 组合模块
│   └── full_pipeline.py  # 意图识别 + 自动路由的完整 AI Pipeline
├── ui/                   # Streamlit 交互界面
│   ├── app.py            # 主入口
│   └── pages/            # 各功能页面
├── config/
│   └── settings.py       # 全局配置
├── data/
│   └── sample_docs/      # 示例文档
└── tests/                # 单元测试
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目后，创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 OpenAI API Key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. 启动交互界面

```bash
streamlit run ui/app.py
```

界面启动后，在浏览器中访问 `http://localhost:8501`

### 4. 命令行运行（可选）

```python
# 示例：使用 RAG Pipeline
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.ingest("./data/sample_docs/")
result = pipeline.query("什么是 RAG？")
print(result["answer"])
```

```python
# 示例：使用 Agent
from agent.agent_core import Agent

agent = Agent()
result = agent.run("北京今天天气怎么样？")
print(result["answer"])
```

## 学习路线

### 阶段 1：Prompt 工程

- **基础技巧**：角色设定、指令明确、上下文提供、格式约束
- **进阶技巧**：Few-shot、Chain-of-Thought、Self-Consistency、Tree-of-Thoughts
- **Agent Prompt**：ReAct 模板、自动 Prompt 工程
- **调试工具**：Prompt 评估、A/B 对比、弱点分析

### 阶段 2：RAG（检索增强生成）

- **文档处理**：加载、分块、向量化
- **检索优化**：相似度搜索、重排序、混合检索
- **生成增强**：上下文构建、引用标注、答案生成
- **完整 Pipeline**：一键完成文档入库到问答

### 阶段 3：Agent（智能体）

- **工具定义**：搜索、计算、天气等可调用工具
- **任务规划**：将复杂请求拆解为可执行步骤
- **执行循环**：思考 -> 行动 -> 观察 -> 再思考
- **记忆管理**：对话历史、上下文窗口

### 阶段 4：完整项目

- **意图识别**：自动判断用户需求类型
- **智能路由**：知识查询走 RAG，工具任务走 Agent
- **统一接口**：封装为完整的 AI 应用

## 核心依赖

| 包名 | 用途 |
|------|------|
| langchain | LLM 应用框架 |
| openai | OpenAI API 调用 |
| chromadb | 向量数据库 |
| sentence-transformers | 本地 Embedding 模型 |
| streamlit | Web 交互界面 |
| duckduckgo-search | 网络搜索 |

## 进阶配置

### 使用本地 Embedding 模型

在 `.env` 中设置或代码中指定：

```python
from rag.embedding import EmbeddingManager

# 使用本地模型（无需 API Key）
embedding = EmbeddingManager(use_local=True)
```

### 接入其他 LLM 提供商

修改 `.env` 中的 `OPENAI_BASE_URL`：

```env
# 使用 Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment

# 使用兼容 OpenAI API 的第三方服务
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

## 常见问题

**Q: 没有 OpenAI API Key 怎么办？**

A: 可以使用本地 Embedding 模型（`use_local=True`），但 LLM 生成部分仍需要 API Key。建议使用国内兼容 OpenAI API 的服务。

**Q: 向量库数据存在哪里？**

A: 默认存储在项目目录下的 `data/chroma_db/` 中，可通过 `.env` 中的 `CHROMA_PERSIST_DIR` 修改。

**Q: 如何添加自定义工具？**

A: 在 `agent/tools/` 目录下新建工具类，继承工具接口，然后在 `agent/tools/__init__.py` 中注册。

## 许可证

MIT License
