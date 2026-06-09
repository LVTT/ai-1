import streamlit as st

from config.settings import SAMPLE_DOCS_DIR, check_api_key
from ui.components.common import api_key_warning

st.set_page_config(page_title="完整项目", page_icon="🚀", layout="wide")

st.title("🚀 完整 AI 项目")

api_key_warning()

st.markdown("""
这是将 **Prompt + RAG + Agent** 组合在一起的完整 AI 应用。
系统会自动识别用户意图，选择最佳处理路径：
- 📚 知识查询 -> 走 RAG
- 🔧 工具任务 -> 走 Agent
- 💬 一般问答 -> 走直接 LLM
""")

# 初始化 session state
if "full_pipeline" not in st.session_state:
    st.session_state.full_pipeline = None
if "pipeline_initialized" not in st.session_state:
    st.session_state.pipeline_initialized = False

# 侧边栏
with st.sidebar:
    st.header("Pipeline 配置")
    force_mode = st.selectbox(
        "强制模式（可选）",
        ["自动选择", "RAG", "Agent", "直接 LLM"],
    )
    force_mode_map = {
        "自动选择": None,
        "RAG": "rag",
        "Agent": "agent",
        "直接 LLM": "llm",
    }

# 主界面
tab1, tab2 = st.tabs(["⚙️ 初始化", "💬 开始对话"])

with tab1:
    st.header("初始化完整 Pipeline")

    st.subheader("1. RAG 知识库")
    docs_path = st.text_input("文档目录", str(SAMPLE_DOCS_DIR))

    col1, col2 = st.columns(2)
    with col1:
        init_rag = st.button("📚 初始化 RAG")
    with col2:
        init_agent = st.button("🤖 初始化 Agent")

    if init_rag:
        if not check_api_key():
            st.error("请配置 API Key")
        else:
            with st.spinner("正在初始化 RAG..."):
                try:
                    from integration.full_pipeline import FullAIPipeline
                    if st.session_state.full_pipeline is None:
                        st.session_state.full_pipeline = FullAIPipeline()
                    st.session_state.full_pipeline.init_rag(docs_path)
                    st.success("✅ RAG 初始化成功！")
                except Exception as e:
                    st.error(f"RAG 初始化失败：{e}")

    if init_agent:
        if not check_api_key():
            st.error("请配置 API Key")
        else:
            with st.spinner("正在初始化 Agent..."):
                try:
                    from integration.full_pipeline import FullAIPipeline
                    if st.session_state.full_pipeline is None:
                        st.session_state.full_pipeline = FullAIPipeline()
                    st.session_state.full_pipeline.init_agent()
                    st.success("✅ Agent 初始化成功！")
                except Exception as e:
                    st.error(f"Agent 初始化失败：{e}")

    # 显示状态
    if st.session_state.full_pipeline:
        status = st.session_state.full_pipeline.get_status()
        st.subheader("当前状态")
        st.json(status)

with tab2:
    st.header("智能对话")
    st.markdown("输入你的问题，系统会自动选择最佳处理方式")

    if st.session_state.full_pipeline is None:
        st.warning("请先初始化至少一个组件（RAG 或 Agent）")
    else:
        query = st.text_input("你的问题", "RAG 和 Agent 有什么区别？")

        if st.button("💬 发送"):
            if not check_api_key():
                st.error("请配置 API Key")
            else:
                with st.spinner("正在处理..."):
                    try:
                        mode = force_mode_map[force_mode]
                        result = st.session_state.full_pipeline.process(
                            query, force_mode=mode)

                        # 显示处理路径
                        path = result.get("mode", "unknown")
                        path_icons = {
                            "rag": "📚",
                            "agent": "🤖",
                            "llm": "💬",
                        }
                        icon = path_icons.get(path, "🔹")
                        st.info(f"处理路径：{icon} {path.upper()}")

                        # 显示回答
                        st.markdown("### 回答")
                        st.markdown(result["answer"])

                        # 显示额外信息
                        if "sources" in result and result["sources"]:
                            with st.expander("参考来源"):
                                for src in result["sources"]:
                                    st.caption(f"📄 {src['source']}")

                        if "steps" in result and result["steps"]:
                            with st.expander("执行步骤"):
                                for step in result["steps"]:
                                    st.markdown(
                                        f"**步骤 {step['iteration']}**: {step.get('thought', '')}")

                    except Exception as e:
                        st.error(f"处理失败：{e}")

    st.divider()
    st.subheader("示例问题")
    examples = [
        "什么是 RAG？（测试知识查询 -> RAG）",
        "北京今天天气怎么样？（测试工具调用 -> Agent）",
        "帮我计算 123 * 456（测试工具调用 -> Agent）",
        "写一首关于 AI 的诗（测试创意生成 -> LLM）",
    ]
    for ex in examples:
        st.caption(f"• {ex}")
