import streamlit as st

from config.settings import check_api_key
from ui.components.common import api_key_warning

st.set_page_config(page_title="Agent 实验室", page_icon="🤖", layout="wide")

st.title("🤖 Agent 实验室")

api_key_warning()

st.markdown("""
Agent（智能体）能够自主感知环境、做出决策并执行动作。
本实验室展示 ReAct 风格的 Agent，观察它如何交替进行 **思考 -> 行动 -> 观察**。
""")

# 初始化 session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

# 侧边栏
with st.sidebar:
    st.header("Agent 配置")
    max_iterations = st.slider("最大迭代次数", 1, 10, 5)

# 主界面
tab1, tab2 = st.tabs(["⚙️ 初始化", "🚀 运行 Agent"])

with tab1:
    st.header("初始化 Agent")
    st.markdown("配置并初始化 Agent，加载可用工具")

    st.subheader("可用工具")
    tools_info = [
        {"名称": "search", "描述": "使用 DuckDuckGo 搜索网络信息", "需要": "无需 API Key"},
        {"名称": "calculator", "描述": "计算数学表达式", "需要": "numexpr"},
        {"名称": "weather", "描述": "查询城市天气（模拟数据）", "需要": "无需额外依赖"},
    ]
    st.dataframe(tools_info, use_container_width=True, hide_index=True)

    if st.button("⚙️ 初始化 Agent"):
        if not check_api_key():
            st.error("请配置 API Key")
        else:
            with st.spinner("正在初始化..."):
                try:
                    from agent.agent_core import Agent
                    agent = Agent(max_iterations=max_iterations)
                    st.session_state.agent = agent
                    st.session_state.agent_initialized = True
                    st.success("✅ Agent 初始化成功！")
                except Exception as e:
                    st.error(f"初始化失败：{e}")

    if st.session_state.agent_initialized:
        st.info("✅ Agent 已就绪")
        if st.button("重置 Agent"):
            st.session_state.agent.reset()
            st.session_state.agent_initialized = False
            st.rerun()

with tab2:
    st.header("运行 Agent")
    st.markdown("输入任务，观察 Agent 的思考-行动-观察循环")

    if not st.session_state.agent_initialized:
        st.warning("请先初始化 Agent")
    else:
        query = st.text_input("任务描述", "搜索一下最新的 AI 新闻，然后告诉我北京今天天气如何")

        col1, col2 = st.columns(2)
        with col1:
            run_normal = st.button("🚀 运行（标准模式）")
        with col2:
            run_stream = st.button("🌊 运行（流式模式）")

        if run_normal:
            with st.spinner("Agent 正在思考..."):
                try:
                    result = st.session_state.agent.run(query)

                    st.markdown(f"### 最终回答\n{result['answer']}")
                    st.caption(f"共迭代 {result['iterations']} 次")

                    with st.expander("查看执行步骤"):
                        for step in result["steps"]:
                            st.markdown(f"**步骤 {step['iteration']}**")
                            st.markdown(f"- 思考：{step.get('thought', '')}")
                            st.markdown(
                                f"- 行动：{step.get('action', '')}({step.get('action_input', '')})")
                            obs = step.get('observation', '')
                            st.markdown(
                                f"- 观察：{obs[:300]}{'...' if len(obs) > 300 else ''}")
                            st.divider()

                except Exception as e:
                    st.error(f"运行失败：{e}")

        if run_stream:
            st.markdown("### 实时执行过程")
            output_container = st.container()
            try:
                for chunk in st.session_state.agent.run_stream(query):
                    output_container.markdown(chunk)
            except Exception as e:
                st.error(f"流式运行失败：{e}")
