"""完整 AI 项目 Pipeline

将 Prompt 工程、RAG、Agent 组合为一个完整的 AI 应用。

Pipeline 流程：
1. 用户输入
2. 意图识别（Prompt 工程）
3. 知识检索（RAG）
4. 工具调用（Agent）
5. 综合生成最终回答
"""

from typing import Dict, Any, Optional, List
from enum import Enum

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL
from rag.pipeline import RAGPipeline
from agent.agent_core import Agent
from prompts.templates import get_task_prompt


class IntentType(Enum):
    """用户意图类型"""
    GENERAL = "general"           # 一般问答
    KNOWLEDGE = "knowledge"       # 知识查询（走 RAG）
    TOOL = "tool"                 # 需要工具（走 Agent）
    CREATIVE = "creative"         # 创意生成
    ANALYSIS = "analysis"         # 分析任务


class FullAIPipeline:
    """完整 AI Pipeline

    根据用户意图自动选择处理路径：
    - 知识查询 -> RAG
    - 工具任务 -> Agent
    - 其他 -> 直接 LLM

    使用示例：
        pipeline = FullAIPipeline()
        pipeline.init_rag("./docs/")
        result = pipeline.process("什么是RAG？")
    """

    INTENT_PROMPT = get_task_prompt("intent")

    def __init__(
        self,
        model: Optional[str] = None,
        rag_pipeline: Optional[RAGPipeline] = None,
        agent: Optional[Agent] = None,
    ):
        self.model = model or DEFAULT_LLM_MODEL
        self.rag = rag_pipeline
        self.agent = agent
        self._client = None

    def _get_client(self):
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

    def init_rag(self, docs_path: str, **kwargs) -> None:
        """初始化 RAG 组件"""
        self.rag = RAGPipeline(**kwargs)
        self.rag.ingest(docs_path)

    def init_agent(self, **kwargs) -> None:
        """初始化 Agent 组件"""
        self.agent = Agent(**kwargs)

    def classify_intent(self, query: str) -> IntentType:
        """意图识别"""
        prompt = self.INTENT_PROMPT.format(query=query)

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20,
        )

        intent_str = response.choices[0].message.content or "general"
        intent_str = intent_str.strip().lower()

        # 映射到枚举
        intent_map = {
            "knowledge": IntentType.KNOWLEDGE,
            "tool": IntentType.TOOL,
            "creative": IntentType.CREATIVE,
            "analysis": IntentType.ANALYSIS,
        }
        return intent_map.get(intent_str, IntentType.GENERAL)

    def process(self, query: str, force_mode: Optional[str] = None) -> Dict[str, Any]:
        """处理用户请求

        Args:
            query: 用户输入
            force_mode: 强制使用指定模式 ("rag", "agent", "llm")

        Returns:
            包含回答和处理路径的结果
        """
        # 确定处理模式
        if force_mode:
            mode = force_mode
        else:
            intent = self.classify_intent(query)
            mode = self._select_mode(intent)

        # 执行对应处理
        if mode == "rag" and self.rag:
            result = self._process_rag(query)
        elif mode == "agent" and self.agent:
            result = self._process_agent(query)
        else:
            result = self._process_llm(query)

        result["query"] = query
        result["mode"] = mode
        return result

    def _select_mode(self, intent: IntentType) -> str:
        """根据意图选择处理模式"""
        if intent == IntentType.KNOWLEDGE and self.rag:
            return "rag"
        elif intent == IntentType.TOOL and self.agent:
            return "agent"
        else:
            return "llm"

    def _process_rag(self, query: str) -> Dict[str, Any]:
        """RAG 处理"""
        rag_result = self.rag.query(query)
        return {
            "answer": rag_result.get("answer", ""),
            "sources": rag_result.get("sources", []),
            "prompt": rag_result.get("prompt", ""),
            "path": "RAG Pipeline",
        }

    def _process_agent(self, query: str) -> Dict[str, Any]:
        """Agent 处理"""
        agent_result = self.agent.run(query)
        return {
            "answer": agent_result.get("answer", ""),
            "steps": agent_result.get("steps", []),
            "iterations": agent_result.get("iterations", 0),
            "path": "Agent Pipeline",
        }

    def _process_llm(self, query: str) -> Dict[str, Any]:
        """直接 LLM 处理"""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=2048,
        )
        answer = response.choices[0].message.content or ""
        return {
            "answer": answer,
            "path": "Direct LLM",
        }

    def chat(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """支持对话历史的聊天接口"""
        messages = history or []
        messages.append({"role": "user", "content": query})

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        answer = response.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": answer})

        return {
            "answer": answer,
            "messages": messages,
            "path": "Chat Mode",
        }

    def get_status(self) -> Dict[str, Any]:
        """获取 Pipeline 状态"""
        return {
            "rag_initialized": self.rag is not None,
            "agent_initialized": self.agent is not None,
            "model": self.model,
        }
