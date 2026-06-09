"""检索器模块

负责从向量库中检索与查询相关的文档。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from rag.embedding import EmbeddingManager
from rag.vector_store import VectorStoreManager


@dataclass
class RetrievedDocument:
    """检索结果文档"""
    content: str
    metadata: Dict[str, Any]
    score: float
    id: str


class Retriever:
    """检索器

    封装 Embedding + VectorStore，提供统一的检索接口。
    """

    def __init__(
        self,
        embedding_manager: Optional[EmbeddingManager] = None,
        vector_store: Optional[VectorStoreManager] = None,
        top_k: int = 4,
    ):
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or VectorStoreManager()
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedDocument]:
        """检索相关文档

        Args:
            query: 查询文本
            top_k: 返回文档数量
            where: 过滤条件

        Returns:
            检索到的文档列表，按相似度排序
        """
        k = top_k or self.top_k

        # 1. 查询向量化
        query_embedding = self.embedding_manager.embed_query(query)

        # 2. 向量检索
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=k,
            where=where,
        )

        # 3. 包装结果
        documents = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                documents.append(RetrievedDocument(
                    content=results["documents"][0][i] or "",
                    metadata=results["metadatas"][0][i] or {},
                    score=results["distances"][0][i] if results["distances"] else 0.0,
                    id=doc_id,
                ))

        return documents

    def retrieve_with_scores(
        self,
        query: str,
        score_threshold: float = 0.5,
        top_k: Optional[int] = None,
    ) -> List[RetrievedDocument]:
        """带分数阈值过滤的检索"""
        docs = self.retrieve(query, top_k=top_k)
        # Chroma 使用 cosine distance，越小越相似
        return [d for d in docs if d.score <= score_threshold]

    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_n: int = 3,
    ) -> List[RetrievedDocument]:
        """简单重排序（基于向量相似度）

        生产环境可使用更专业的重排序模型，如：
        - Cohere Rerank
        - BGE Reranker
        - 交叉编码器 (Cross-Encoder)
        """
        if not documents:
            return []

        query_vec = self.embedding_manager.embed_query(query)

        scored_docs = []
        for doc in documents:
            doc_vec = self.embedding_manager.embed_query(doc.content)
            sim = self.embedding_manager.similarity(query_vec, doc_vec)
            scored_docs.append((sim, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_n]]
