"""重排序模块

使用 Cross-Encoder 对向量检索结果进行精准重排序，提升检索质量。
"""

from typing import List
import os

# 使用 HuggingFace 国内镜像
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# 模块级全局缓存
_global_reranker = None


class Reranker:
    """Cross-Encoder 重排序器

    将查询和文档拼接后输入模型，得到更精确的匹配分数。
    比纯向量相似度更准，但速度较慢，建议只对 top_k 结果重排。
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        """获取重排序模型（模块级缓存）"""
        global _global_reranker
        if _global_reranker is not None:
            return _global_reranker
        if self._model is not None:
            _global_reranker = self._model
            return _global_reranker

        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            raise ImportError(
                "请安装 sentence-transformers: pip install sentence-transformers")

        print(f"正在加载重排序模型: {self.model_name}...")
        print("首次使用需下载模型（约 400MB），请耐心等待...")
        self._model = CrossEncoder(self.model_name)
        _global_reranker = self._model
        print(f"重排序模型加载完成: {self.model_name}")
        return self._model

    def rerank(self, query: str, documents: List[str], top_n: int = 4) -> List[int]:
        """对文档列表进行重排序

        Args:
            query: 查询文本
            documents: 文档内容列表
            top_n: 返回前 N 个结果的索引

        Returns:
            按相关性排序的文档索引列表
        """
        if not documents:
            return []

        model = self._get_model()
        pairs = [[query, doc] for doc in documents]
        scores = model.predict(pairs)

        # 分数越高越相关，按分数降序排列
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return [idx for idx, _ in indexed_scores[:top_n]]
