import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import SAMPLE_DOCS_DIR, check_api_key
from ui.components.common import api_key_warning

st.set_page_config(page_title="RAG 实验室", page_icon="🔍", layout="wide")

st.title("🔍 RAG 实验室")

api_key_warning()

st.markdown("""
RAG（检索增强生成）通过从知识库中检索相关文档，增强 LLM 的回答质量。
本实验室提供完整的 RAG Pipeline 交互式体验。
""")

# 初始化 session state
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "rag_initialized" not in st.session_state:
    st.session_state.rag_initialized = False

# 侧边栏配置
with st.sidebar:
    st.header("RAG 配置")
    chunk_size = st.slider("分块大小", 200, 2000, 1000, 100)
    chunk_overlap = st.slider("重叠大小", 0, 500, 200, 50)
    top_k = st.slider("检索数量", 1, 10, 4)
    use_local = st.checkbox("使用本地 Embedding（无需 API，需下载模型）", value=False)

# 主界面
tab1, tab2, tab3 = st.tabs(["📚 文档入库", "🔎 检索测试", "💬 完整问答"])

with tab1:
    st.header("文档入库")
    st.markdown("选择要加载的文档目录，系统将自动完成：加载 -> 分块 -> 向量化 -> 存储")

    docs_path = st.text_input("文档目录", str(SAMPLE_DOCS_DIR))

    if st.button("🚀 开始入库"):
        if not check_api_key() and not use_local:
            st.error("请配置 API Key 或启用本地 Embedding")
        else:
            with st.spinner("正在初始化 RAG Pipeline..."):
                try:
                    from rag.pipeline import RAGPipeline
                    pipeline = RAGPipeline(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        top_k=top_k,
                        use_local_embedding=use_local,
                    )
                    result = pipeline.ingest(docs_path)

                    if result["status"] == "success":
                        st.session_state.rag_pipeline = pipeline
                        st.session_state.rag_initialized = True
                        st.success(f"✅ 入库成功！共处理 {result['chunks_ingested']} 个文档块")
                        st.json(result["vector_store_stats"])
                    else:
                        st.error(result["message"])
                except Exception as e:
                    st.error(f"入库失败：{e}")

    if st.session_state.rag_initialized:
        st.info("✅ RAG 已初始化，可以前往其他标签页进行测试")
        if st.button("清空向量库"):
            st.session_state.rag_pipeline.clear()
            st.session_state.rag_initialized = False
            st.rerun()

with tab2:
    st.header("检索测试")
    st.markdown("测试向量检索效果，查看召回的文档片段")

    if not st.session_state.rag_initialized:
        st.warning("请先完成文档入库")
    else:
        query = st.text_input("检索查询", "什么是 RAG？")

        if st.button("🔎 检索"):
            with st.spinner("正在检索..."):
                try:
                    docs = st.session_state.rag_pipeline.query_only_retrieve(query, top_k=top_k)
                    st.success(f"检索到 {len(docs)} 条结果")

                    for i, doc in enumerate(docs, 1):
                        with st.container(border=True):
                            st.markdown(f"**结果 {i}** | 相似度分数: {doc.score:.4f}")
                            source = doc.metadata.get("file_name", "未知")
                            st.caption(f"来源：{source}")
                            st.markdown(doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)
                except Exception as e:
                    st.error(f"检索失败：{e}")

with tab3:
    st.header("完整问答")
    st.markdown("输入问题，系统将先检索相关知识，再生成带引用的回答")

    if not st.session_state.rag_initialized:
        st.warning("请先完成文档入库")
    else:
        query = st.text_input("你的问题", "RAG 有哪些优势？")

        if st.button("💬 生成回答"):
            with st.spinner("正在检索和生成..."):
                try:
                    result = st.session_state.rag_pipeline.query(query, return_sources=True)

                    st.markdown("### 回答")
                    st.markdown(result["answer"])

                    if result.get("sources"):
                        st.markdown("### 参考来源")
                        for src in result["sources"]:
                            st.caption(f"📄 {src['source']} (score: {src['score']:.4f})")

                    with st.expander("查看完整 Prompt"):
                        st.code(result.get("prompt", ""), language="text")
                except Exception as e:
                    st.error(f"生成失败：{e}")
