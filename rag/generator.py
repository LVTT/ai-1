"""生成器模块

基于检索到的上下文，调用 LLM 生成回答。
"""

from typing import List, Optional, Dict, Any

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL
from rag.retriever import RetrievedDocument


class Generator:
    """RAG 生成器

    负责构建 Prompt 并调用 LLM 生成最终回答。
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.model = model or DEFAULT_LLM_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
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

    def build_prompt(
        self,
        query: str,
        documents: List[RetrievedDocument],
        system_prompt: Optional[str] = None,
    ) -> str:
        """构建 RAG Prompt

        格式：
        系统指令（可选）
        上下文
        用户问题
        """
        # 组装上下文
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get(
                "file_name", doc.metadata.get("source", "未知"))
            chunk_idx = doc.metadata.get("chunk_index", 0)
            total = doc.metadata.get("total_chunks", 1)
            pos = doc.metadata.get("position_percent", 0)
            context_parts.append(
                f"[文档 {i}]（来源：{source} | 第 {chunk_idx+1}/{total} 块 | 位置约 {pos}%）\n{doc.content}\n"
            )
        context = "\n".join(context_parts)

        # 组装完整 Prompt
        prompt = f"""基于以下参考资料回答问题。如果资料中没有相关信息，请明确说明"根据提供的资料无法回答"。

--- 参考资料 ---
{context}
--- 参考资料结束 ---

问题：{query}

请根据参考资料给出准确、简洁的回答："""

        return prompt

    def generate(
        self,
        query: str,
        documents: List[RetrievedDocument],
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """生成回答"""
        prompt = self.build_prompt(query, documents, system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=stream,
        )

        if stream:
            return response  # 返回流式迭代器

        return response.choices[0].message.content or ""

    def generate_with_citation(
        self,
        query: str,
        documents: List[RetrievedDocument],
    ) -> Dict[str, Any]:
        """生成带引用的回答

        要求模型在回答中标注信息来源。
        """
        # 构建带引用要求的 Prompt
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get(
                "file_name", doc.metadata.get("source", "未知"))
            chunk_idx = doc.metadata.get("chunk_index", 0)
            total = doc.metadata.get("total_chunks", 1)
            pos = doc.metadata.get("position_percent", 0)
            context_parts.append(
                f"[文档 {i}]（来源：{source} | 第 {chunk_idx+1}/{total} 块 | 位置约 {pos}%）\n{doc.content}\n"
            )
        context = "\n".join(context_parts)

        prompt = f"""基于以下参考资料回答问题，并在回答中标注信息来源（如 [文档1]、[文档2] 等）。
如果资料中没有相关信息，请明确说明。

--- 参考资料 ---
{context}
--- 参考资料结束 ---

问题：{query}

请给出带引用标注的回答："""

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        answer = response.choices[0].message.content or ""

        return {
            "answer": answer,
            "sources": [
                {
                    "id": doc.id,
                    "source": doc.metadata.get("file_name", doc.metadata.get("source", "未知")),
                    "chunk": f"{doc.metadata.get('chunk_index', 0) + 1}/{doc.metadata.get('total_chunks', 1)}",
                    "position": f"{doc.metadata.get('position_percent', 0)}%",
                    "score": doc.score,
                }
                for doc in documents
            ],
            "prompt": prompt,
        }
