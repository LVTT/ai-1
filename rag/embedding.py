"""Embedding 向量化模块

负责将文本转换为向量表示。
"""

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, EMBEDDING_MODEL
import numpy as np
from typing import List, Optional
import os

# 使用 HuggingFace 国内镜像，避免模型下载超时
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


class EmbeddingManager:
    """Embedding 管理器

    支持两种模式：
    1. OpenAI API（推荐，需要 API Key）
    2. 本地 sentence-transformers（无需 API，但需下载模型）
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_local: bool = False,
    ):
        self.model_name = model_name or EMBEDDING_MODEL
        self.use_local = use_local
        self._local_model = None
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")

            self._client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
            )
        return self._client

    def _get_local_model(self):
        """获取本地 embedding 模型"""
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "请安装 sentence-transformers: pip install sentence-transformers")

            # 强制使用中文模型（BAAI/bge-small-zh-v1.5 约 100MB，速度快且中文效果好）
            model_name = "BAAI/bge-small-zh-v1.5"
            print(f"正在加载本地模型: {model_name}...")
            print("首次使用需下载模型（约 100MB），请耐心等待...")
            self._local_model = SentenceTransformer(model_name)
            print(f"模型加载完成: {model_name}")
        return self._local_model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量列表"""
        if not texts:
            return []

        if self.use_local:
            return self._embed_local(texts)
        else:
            return self._embed_api(texts)

    def embed_query(self, text: str) -> List[float]:
        """将单个查询文本转换为向量"""
        results = self.embed_texts([text])
        return results[0] if results else []

    def _embed_api(self, texts: List[str]) -> List[List[float]]:
        """使用 OpenAI API 进行向量化"""
        client = self._get_client()

        # OpenAI embedding API 有批量限制
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            response = client.embeddings.create(
                model=self.model_name,
                input=batch,
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

        return all_embeddings

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """使用本地模型进行向量化"""
        model = self._get_local_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
