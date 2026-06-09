"""Streamlit 主应用入口"""

import streamlit as st
from config.settings import check_api_key

st.set_page_config(
    page_title="AI 工程化实验室",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🧪 AI 工程化实验室")

st.markdown("""
欢迎来到 **AI 工程化实验室**！这是一个用于学习和实践 AI 工程化技术的交互式平台。

## 🎯 项目目标

本项目按照 **Prompt -> RAG -> Agent -> 完整项目** 的路线，帮助你一步步掌握 AI 工程化的核心技术。

## 📚 模块导览

| 模块 | 说明 | 状态 |
|------|------|------|
| 📝 Prompt 实验室 | 学习和调试各种 Prompt 工程技巧 | ✅ |
| 🔍 RAG 实验室 | 体验检索增强生成的完整流程 | ✅ |
| 🤖 Agent 实验室 | 探索智能体的思考与行动循环 | ✅ |
| 🚀 完整项目 | 组合所有模块的完整 AI 应用 | ✅ |

## 🚀 快速开始

1. 在左侧导航栏选择要学习的模块
2. 每个模块都包含理论说明、代码示例和交互式调试界面
3. 建议按照 Prompt -> RAG -> Agent 的顺序逐步学习

## ⚙️ 环境配置

在使用前，请确保已配置 API Key：

1. 复制 `.env.example` 为 `.env`
2. 填写你的 `OPENAI_API_KEY`
3. 运行 `pip install -r requirements.txt` 安装依赖
4. 启动界面：`streamlit run ui/app.py`
""")

# API Key 状态检查
st.divider()
if check_api_key():
    st.success("✅ API Key 已配置")
else:
    st.error("❌ API Key 未配置")
    st.info("请复制 `.env.example` 为 `.env`，并填写你的 OPENAI_API_KEY")

# 项目结构展示
st.divider()
st.subheader("📁 项目结构")

st.code("""
ai-engineering-lab/
├── prompts/              # Prompt 工程模块
│   ├── basics.py         # 基础 Prompt 技巧
│   ├── advanced.py       # 进阶 Prompt 技巧
│   ├── debug_tools.py    # Prompt 调试工具
│   └── templates/        # Prompt 模板库
├── rag/                  # RAG 模块
│   ├── document_loader.py
│   ├── embedding.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── generator.py
│   └── pipeline.py
├── agent/                # Agent 模块
│   ├── tools/
│   ├── planner.py
│   ├── executor.py
│   ├── memory.py
│   └── agent_core.py
├── integration/          # 组合模块
│   └── full_pipeline.py
└── ui/                   # Streamlit 界面
    ├── app.py
    └── pages/
""", language="text")
