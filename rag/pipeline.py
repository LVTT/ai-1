"""RAG Pipeline 完整流程

封装文档加载 -> 分块 -> 向量化 -> 存储 -> 检索 -> 生成的完整流程。
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from rag.document_loader import DocumentLoader, Document
from rag.embedding import EmbeddingManager
from rag.vector_store import VectorStoreManager
from rag.retriever import Retriever, RetrievedDocument
from rag.generator import Generator


class RAGPipeline:
    """RAG 完整 Pipeline

    使用示例：
        pipeline = RAGPipeline()
        pipeline.ingest("./docs/")
        result = pipeline.query("什么是RAG？")
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_manager: Optional[EmbeddingManager] = None,
        vector_store: Optional[VectorStoreManager] = None,
        generator: Optional[Generator] = None,
        top_k: int = 4,
        use_local_embedding: bool = False,
    ):
        self.document_loader = DocumentLoader(chunk_size, chunk_overlap)
        self.embedding_manager = embedding_manager or EmbeddingManager(
            use_local=use_local_embedding
        )
        self.vector_store = vector_store or VectorStoreManager()
        self.retriever = Retriever(
            embedding_manager=self.embedding_manager,
            vector_store=self.vector_store,
            top_k=top_k,
        )
        self.generator = generator or Generator()

    def ingest(
        self,
        source: Union[str, Path],
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """文档入库流程

        1. 加载文档
        2. 分块
        3. 向量化
        4. 存入向量库
        """
        # 如需切换 collection
        if collection_name:
            self.vector_store = VectorStoreManager(
                collection_name=collection_name)
            self.retriever.vector_store = self.vector_store

        print(f"[RAG] 正在加载文档: {source}")
        documents = self.document_loader.load_and_split(source)
        print(f"[RAG] 加载完成，共 {len(documents)} 个文档块")

        if not documents:
            return {"status": "error", "message": "未找到可加载的文档"}

        # 提取文本和元数据
        texts = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        print(f"[RAG] 正在向量化...")
        embeddings = self.embedding_manager.embed_texts(texts)
        print(f"[RAG] 向量化完成")

        print(f"[RAG] 正在存入向量库...")
        self.vector_store.add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        stats = self.vector_store.get_stats()
        print(f"[RAG] 入库完成，当前库中共有 {stats['document_count']} 条记录")

        return {
            "status": "success",
            "chunks_ingested": len(documents),
            "vector_store_stats": stats,
        }

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        return_sources: bool = True,
    ) -> Dict[str, Any]:
        """查询流程

        1. 检索相关文档
        2. 构建 Prompt
        3. 生成回答
        """
        print(f"[RAG] 查询: {query}")

        # 检索
        documents = self.retriever.retrieve(query, top_k=top_k)
        print(f"[RAG] 检索到 {len(documents)} 条相关文档")

        if not documents:
            return {
                "answer": "未能检索到相关文档，无法回答该问题。",
                "sources": [],
            }

        # 生成
        if return_sources:
            result = self.generator.generate_with_citation(query, documents)
        else:
            answer = self.generator.generate(query, documents)
            result = {"answer": answer, "sources": []}

        return result

    def query_only_retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[RetrievedDocument]:
        """仅检索，不生成（用于调试检索效果）"""
        return self.retriever.retrieve(query, top_k=top_k)

    def clear(self) -> None:
        """清空向量库"""
        self.vector_store.delete_collection()
        print("[RAG] 向量库已清空")

    def get_stats(self) -> Dict[str, Any]:
        """获取 Pipeline 状态"""
        return {
            "vector_store": self.vector_store.get_stats(),
            "document_loader": {
                "chunk_size": self.document_loader.chunk_size,
                "chunk_overlap": self.document_loader.chunk_overlap,
            },
        }
