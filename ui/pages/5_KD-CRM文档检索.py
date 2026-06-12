import re
import html as html_module

import streamlit as st

from config.settings import KD_CRM_DOCS_DIR, check_api_key
from ui.components.common import api_key_warning


def _highlight_text(text: str, query: str) -> str:
    """高亮文档片段中与查询相关的关键词"""
    if not query or not text:
        return html_module.escape(text)

    # 提取查询中的关键词（过滤掉太短的和常见停用词）
    stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
                  "会", "着", "没有", "看", "好", "自己", "这", "那", "什么", "怎么", "吗", "呢", "吧", "啊", "吗", "么", "如何", "哪些", "哪个", "谁", "几", "多少"}
    words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]+', query)
    keywords = [w for w in words if w.lower(
    ) not in stop_words and len(w) >= 2]

    if not keywords:
        return html_module.escape(text)

    # 先转义 HTML
    escaped = html_module.escape(text)

    # 高亮关键词（按长度降序，避免短词干扰长词）
    highlighted = escaped
    for kw in sorted(set(keywords), key=len, reverse=True):
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        highlighted = pattern.sub(
            f'<mark style="background-color: #ffeb3b; color: #000; padding: 1px 3px; border-radius: 3px; font-weight: 600;">{kw}</mark>',
            highlighted
        )
    return highlighted


def _score_label(score: float) -> str:
    """根据相似度分数返回匹配度说明"""
    if score >= 0.8:
        return "🔥 高度相关"
    elif score >= 0.6:
        return "⭐ 中度相关"
    elif score >= 0.4:
        return "📌 低度相关"
    else:
        return "📎 弱相关"


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
if "kd_crm_user_cleared" not in st.session_state:
    st.session_state.kd_crm_user_cleared = False
if "use_rerank" not in st.session_state:
    st.session_state.use_rerank = False

# 自动检测：用户未手动清空过，且向量库有数据，则自动恢复
if not st.session_state.kd_crm_initialized and not st.session_state.kd_crm_user_cleared:
    try:
        from rag.vector_store import VectorStoreManager
        vs = VectorStoreManager(collection_name="kd_crm")
        stats = vs.get_stats()
        count = stats.get("document_count", 0)
        st.session_state.kd_crm_detected_count = count
        if count > 0:
            from rag.pipeline import RAGPipeline
            from rag.vector_store import VectorStoreManager
            from rag.reranker import Reranker
            pipeline = RAGPipeline(
                chunk_size=1000,
                chunk_overlap=200,
                top_k=4,
                use_local_embedding=True,
                reranker=Reranker() if st.session_state.use_rerank else None,
            )
            # 切换到 kd_crm collection（默认是 default，必须显式切换）
            pipeline.vector_store = VectorStoreManager(
                collection_name="kd_crm")
            pipeline.retriever.vector_store = pipeline.vector_store
            st.session_state.kd_crm_pipeline = pipeline
            st.session_state.kd_crm_initialized = True
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

    use_rerank = st.checkbox("启用重排序（更精准，首次需下载约 400MB 模型）",
                             value=st.session_state.use_rerank)
    st.session_state.use_rerank = use_rerank
    if use_rerank:
        st.info("🔄 首次使用会自动下载中文重排序模型（约 400MB），请保持网络畅通，等待 2-5 分钟")

    st.markdown("---")
    st.header("🔍 需求追溯过滤")
    filter_file_keyword = st.text_input(
        "文件名关键词", "", placeholder="如：赵青青、报价、2024")

    # 动态获取过滤选项（从向量库 metadata 中提取）
    all_years = []
    all_modules = []
    all_people = []
    if st.session_state.kd_crm_initialized and st.session_state.kd_crm_pipeline:
        try:
            stats = st.session_state.kd_crm_pipeline.vector_store.get_stats()
            # 获取样本 metadata 来构建选项（简化处理）
            # 由于无法直接枚举所有 metadata，使用预定义 + 动态检测
            pass
        except Exception:
            pass

    filter_years = st.multiselect(
        "按年份", ["2022", "2023", "2024", "2025", "2026"], default=[])
    filter_modules = st.multiselect(
        "按模块", ["CRM", "销售系统", "办公系统", "费用管理", "报价"], default=[])
    filter_people = st.multiselect(
        "按涉及人", ["赵青青", "刘新颖", "钱金玉", "杜广宁", "仲逸明"], default=[])

# 主界面
st.info(f"📁 默认文档目录：{KD_CRM_DOCS_DIR}")

tab1, tab2, tab3 = st.tabs(["📚 文档入库", "🔎 检索测试", "💬 知识问答"])

with tab1:
    st.header("CRM 文档入库")
    st.markdown("将 KD-CRM 相关文档放入目录后，点击入库按钮完成：加载 → 分块 → 向量化 → 存储")

    # 检测到历史数据但未初始化时，显示恢复提示（仅用户手动清空后才会出现）
    if not st.session_state.kd_crm_initialized and st.session_state.kd_crm_detected_count > 0:
        st.warning(
            f"⚠️ 检测到向量库中有 {st.session_state.kd_crm_detected_count} 条历史数据，但当前未加载。")
        if st.button("🔄 恢复使用历史索引"):
            with st.spinner("正在恢复索引..."):
                try:
                    from rag.pipeline import RAGPipeline
                    from rag.vector_store import VectorStoreManager
                    from rag.reranker import Reranker
                    pipeline = RAGPipeline(
                        chunk_size=1000,
                        chunk_overlap=200,
                        top_k=4,
                        use_local_embedding=True,
                        reranker=Reranker() if st.session_state.use_rerank else None,
                    )
                    pipeline.vector_store = VectorStoreManager(
                        collection_name="kd_crm")
                    pipeline.retriever.vector_store = pipeline.vector_store
                    st.session_state.kd_crm_pipeline = pipeline
                    st.session_state.kd_crm_initialized = True
                    st.session_state.kd_crm_user_cleared = False
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
                    from rag.reranker import Reranker
                    pipeline = RAGPipeline(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        top_k=top_k,
                        use_local_embedding=use_local,
                        reranker=Reranker() if st.session_state.use_rerank else None,
                    )
                    result = pipeline.ingest(
                        docs_path, collection_name="kd_crm")

                    if result["status"] == "success":
                        st.session_state.kd_crm_pipeline = pipeline
                        st.session_state.kd_crm_initialized = True
                        st.session_state.kd_crm_user_cleared = False
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
            st.session_state.kd_crm_user_cleared = True
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

                    # 应用过滤器
                    filtered = []
                    for d in docs:
                        fn = d.metadata.get("file_name", "")
                        year = d.metadata.get("year", "")
                        module = d.metadata.get("module", "")
                        people = d.metadata.get("people", "")

                        if filter_file_keyword and filter_file_keyword not in fn:
                            continue
                        if filter_years and year not in filter_years:
                            continue
                        if filter_modules and module not in filter_modules:
                            continue
                        if filter_people and not any(p in people for p in filter_people):
                            continue
                        filtered.append(d)

                    docs = filtered
                    st.success(f"检索到 {len(docs)} 条结果")

                    for i, doc in enumerate(docs, 1):
                        with st.container(border=True):
                            label = _score_label(doc.score)
                            st.markdown(
                                f"**结果 {i}** | {label} | 相似度: {doc.score:.4f}")
                            source = doc.metadata.get("file_name", "未知")
                            chunk = f"{doc.metadata.get('chunk_index', 0) + 1}/{doc.metadata.get('total_chunks', 1)}"
                            pos = f"{doc.metadata.get('position_percent', 0)}%"
                            st.caption(f"📄 {source} | 第 {chunk} 块 | 位置约 {pos}")

                            # 显示需求追溯元数据标签
                            tags = []
                            if doc.metadata.get("year"):
                                tags.append(f"📅 {doc.metadata['year']}")
                            if doc.metadata.get("module"):
                                tags.append(f"🏷️ {doc.metadata['module']}")
                            if doc.metadata.get("people"):
                                tags.append(f"👤 {doc.metadata['people']}")
                            if doc.metadata.get("versions"):
                                tags.append(f"🔀 {doc.metadata['versions']}")
                            if doc.metadata.get("statuses"):
                                tags.append(f"✅ {doc.metadata['statuses']}")
                            if tags:
                                st.caption(" | ".join(tags))

                            # 高亮显示匹配关键词
                            display_text = doc.content[:600] + "..." if len(
                                doc.content) > 600 else doc.content
                            highlighted = _highlight_text(display_text, query)
                            st.markdown(
                                f"<div style='line-height: 1.7;'>{highlighted}</div>", unsafe_allow_html=True)
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
