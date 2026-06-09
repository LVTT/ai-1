"""向量存储模块

使用 ChromaDB 作为向量数据库，支持文档的存储和检索。
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import CHROMA_PERSIST_DIR


class VectorStoreManager:
    """向量存储管理器

    基于 ChromaDB 实现文档的向量化存储和相似度检索。
    """

    def __init__(self, persist_dir: Optional[str] = None, collection_name: str = "default"):
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _get_client(self):
        """获取 ChromaDB 客户端"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
            except ImportError:
                raise ImportError("请安装 chromadb: pip install chromadb")

            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )

        return self._client

    def _get_collection(self):
        """获取或创建集合"""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """添加文档到向量库

        Args:
            documents: 文档内容列表
            embeddings: 对应的向量列表
            metadatas: 元数据列表
            ids: 自定义 ID 列表
        """
        collection = self._get_collection()

        if ids is None:
            # 自动生成 ID
            existing = collection.count()
            ids = [f"doc_{existing + i}" for i in range(len(documents))]

        if metadatas is None:
            metadatas = [{} for _ in documents]

        # ChromaDB 批量添加
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            collection.add(
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end],
            )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 4,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """向量相似度检索

        Returns:
            {
                "ids": [["doc_1", "doc_2"]],
                "distances": [[0.1, 0.2]],
                "documents": [["内容1", "内容2"]],
                "metadatas": [[{"key": "val"}]],
            }
        """
        collection = self._get_collection()

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)
        return results

    def delete_collection(self) -> None:
        """删除当前集合"""
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = None

    def get_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        collection = self._get_collection()
        return {
            "collection_name": self.collection_name,
            "document_count": collection.count(),
            "persist_dir": self.persist_dir,
        }
