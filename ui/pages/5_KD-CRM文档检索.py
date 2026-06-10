import streamlit as st

from config.settings import KD_CRM_DOCS_DIR, check_api_key
from ui.components.common import api_key_warning

st.set_page_config(page_title="KD-CRM 文档检索（原始需求回溯）",
                   page_icon="📋", layout="wide")

st.title("📋 KD-CRM 文档检索（原始需求回溯）")

api_key_warning()

st.markdown("""
KD-CRM 文档检索是基于 RAG 技术的企业知识库问答系统。
上传 CRM 相关文档后，系统会自动建立向量索引，支持自然语言查询产品功能、销售规范、服务手册等内容。
""")

# 初始化 session state（使用独立的 key，避免和 RAG 实验室冲突）
if "kd_crm_pipeline" not in st.session_state:
    st.session_state.kd_crm_pipeline = None
if "kd_crm_initialized" not in st.session_state:
    st.session_state.kd_crm_initialized = False
if "kd_crm_detected_count" not in st.session_state:
    st.session_state.kd_crm_detected_count = 0

# 自动检测：如果向量库中已有 kd_crm 数据，显示恢复提示（不自动恢复，避免清空后"复活"）
if not st.session_state.kd_crm_initialized:
    try:
        from rag.vector_store import VectorStoreManager
        vs = VectorStoreManager(collection_name="kd_crm")
        stats = vs.get_stats()
        st.session_state.kd_crm_detected_count = stats.get("document_count", 0)
    except Exception:
        st.session_state.kd_crm_detected_count = 0

# 侧边栏配置
with st.sidebar:
    st.header("检索配置")
    chunk_size = st.slider("分块大小", 200, 2000, 1000, 100)
    chunk_overlap = st.slider("重叠大小", 0, 500, 200, 50)
    top_k = st.slider("检索数量", 1, 10, 4)
    use_local = st.checkbox(
        "使用本地 Embedding（无需 API，首次需下载约 100MB 模型）", value=False)
    if use_local:
        st.info("🔄 首次使用会自动下载中文 Embedding 模型（约 100MB），请保持网络畅通，等待 1-3 分钟")

# 主界面
st.info(f"📁 默认文档目录：{KD_CRM_DOCS_DIR}")

tab1, tab2, tab3 = st.tabs(["📚 文档入库", "🔎 检索测试", "💬 知识问答"])

with tab1:
    st.header("CRM 文档入库")
    st.markdown("将 KD-CRM 相关文档放入目录后，点击入库按钮完成：加载 → 分块 → 向量化 → 存储")

    # 检测到历史数据但未初始化时，显示恢复提示
    if not st.session_state.kd_crm_initialized and st.session_state.kd_crm_detected_count > 0:
        st.warning(
            f"⚠️ 检测到向量库中有 {st.session_state.kd_crm_detected_count} 条历史数据，但当前未加载。")
        if st.button("🔄 恢复使用历史索引"):
            with st.spinner("正在恢复索引..."):
                try:
                    from rag.pipeline import RAGPipeline
                    pipeline = RAGPipeline(
                        chunk_size=1000,
                        chunk_overlap=200,
                        top_k=4,
                        use_local_embedding=True,
                    )
                    st.session_state.kd_crm_pipeline = pipeline
                    st.session_state.kd_crm_initialized = True
                    st.rerun()
                except Exception as e:
                    st.error(f"恢复失败：{e}")

    docs_path = st.text_input("文档目录", str(KD_CRM_DOCS_DIR))

    if st.button("🚀 开始入库"):
        if not check_api_key() and not use_local:
            st.error("请配置 API Key 或启用本地 Embedding")
        else:
            with st.spinner("正在初始化 KD-CRM 文档索引..."):
                try:
                    from rag.pipeline import RAGPipeline
                    pipeline = RAGPipeline(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        top_k=top_k,
                        use_local_embedding=use_local,
                    )
                    result = pipeline.ingest(
                        docs_path, collection_name="kd_crm")

                    if result["status"] == "success":
                        st.session_state.kd_crm_pipeline = pipeline
                        st.session_state.kd_crm_initialized = True
                        st.success(
                            f"✅ 入库成功！共处理 {result['chunks_ingested']} 个文档块")
                        st.json(result["vector_store_stats"])
                    else:
                        st.error(result["message"])
                except Exception as e:
                    st.error(f"入库失败：{e}")

    if st.session_state.kd_crm_initialized:
        st.info("✅ KD-CRM 文档索引已就绪，可以前往其他标签页进行检索和问答")
        if st.button("清空向量库"):
            try:
                st.session_state.kd_crm_pipeline.clear()
            except Exception as e:
                st.error(f"清空失败：{e}")
            st.session_state.kd_crm_pipeline = None
            st.session_state.kd_crm_initialized = False
            st.session_state.kd_crm_detected_count = 0
            st.rerun()

with tab2:
    st.header("CRM 文档检索测试")
    st.markdown("测试向量检索效果，查看召回的 CRM 文档片段")

    if not st.session_state.kd_crm_initialized:
        st.warning("请先完成文档入库")
    else:
        query = st.text_input("检索查询", "客户分级规则是什么？")

        if st.button("🔎 检索"):
            with st.spinner("正在检索..."):
                try:
                    docs = st.session_state.kd_crm_pipeline.query_only_retrieve(
                        query, top_k=top_k)
                    st.success(f"检索到 {len(docs)} 条结果")

                    for i, doc in enumerate(docs, 1):
                        with st.container(border=True):
                            st.markdown(f"**结果 {i}** | 相似度分数: {doc.score:.4f}")
                            source = doc.metadata.get("file_name", "未知")
                            chunk = f"{doc.metadata.get('chunk_index', 0) + 1}/{doc.metadata.get('total_chunks', 1)}"
                            pos = f"{doc.metadata.get('position_percent', 0)}%"
                            st.caption(f"📄 {source} | 第 {chunk} 块 | 位置约 {pos}")
                            st.markdown(
                                doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)
                except Exception as e:
                    st.error(f"检索失败：{e}")

with tab3:
    st.header("CRM 知识问答")
    st.markdown("输入问题，系统将先检索 KD-CRM 知识库，再生成带引用的回答")

    if not st.session_state.kd_crm_initialized:
        st.warning("请先完成文档入库")
    else:
        query = st.text_input("你的问题", "A 类客户的服务响应时间是多少？")

        if st.button("💬 生成回答"):
            with st.spinner("正在检索和生成..."):
                try:
                    result = st.session_state.kd_crm_pipeline.query(
                        query, return_sources=True)

                    st.markdown("### 回答")
                    st.markdown(result["answer"])

                    if result.get("sources"):
                        st.markdown("### 参考来源")
                        for src in result["sources"]:
                            chunk = src.get("chunk", "")
                            pos = src.get("position", "")
                            st.caption(
                                f"📄 {src['source']} | 第 {chunk} 块 | 位置约 {pos} (score: {src['score']:.4f})")

                    with st.expander("查看完整 Prompt"):
                        st.code(result.get("prompt", ""), language="text")
                except Exception as e:
                    st.error(f"生成失败：{e}")
