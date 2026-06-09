"""Agent 核心模块

整合规划、执行、记忆，实现完整的 ReAct 风格 Agent。
"""

import json
from typing import List, Dict, Any, Optional, Generator as Gen

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL, MAX_AGENT_ITERATIONS
from agent.tools import ToolRegistry, get_default_tools
from agent.planner import TaskPlanner
from agent.executor import ToolExecutor
from agent.memory import ConversationMemory


class Agent:
    """ReAct 风格 Agent

    核心循环：
    1. 观察（Observation）
    2. 思考（Thought）
    3. 行动（Action）
    4. 执行工具
    5. 回到步骤 1

    使用示例：
        agent = Agent()
        result = agent.run("北京今天的天气怎么样？")
    """

    REACT_PROMPT = """你是一个智能助手，可以使用工具来解决问题。

可用的工具：
{tools_description}

请按照以下格式思考并行动（每一步只输出一个 JSON）：
{{
  "thought": "分析当前情况，决定下一步行动",
  "action": "工具名称（或 'finish' 表示完成任务）",
  "action_input": "工具的输入参数（或最终答案）"
}}

注意：
- 如果问题可以直接回答，action 填 "finish"
- 如果需要信息，使用相应工具
- 每次只输出一个 JSON，不要输出多余内容

当前问题：{query}

{history}

请输出下一步（JSON 格式）："""

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        model: Optional[str] = None,
        max_iterations: int = MAX_AGENT_ITERATIONS,
        memory: Optional[ConversationMemory] = None,
    ):
        self.tool_registry = tool_registry or get_default_tools()
        self.model = model or DEFAULT_LLM_MODEL
        self.max_iterations = max_iterations
        self.memory = memory or ConversationMemory()
        self.planner = TaskPlanner(model)
        self.executor = ToolExecutor(self.tool_registry)
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

    def run(self, query: str) -> Dict[str, Any]:
        """运行 Agent 处理查询

        Returns:
            {
                "query": 原始查询,
                "answer": 最终回答,
                "steps": 执行步骤列表,
                "iterations": 迭代次数,
                "history": 执行历史,
            }
        """
        self.memory.add_user_message(query)
        steps = []

        for i in range(self.max_iterations):
            # 构建当前上下文
            history = self._build_history()
            tools_desc = self.tool_registry.get_tool_descriptions()

            prompt = self.REACT_PROMPT.format(
                tools_description=tools_desc,
                query=query,
                history=history,
            )

            # 调用 LLM
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )

            content = response.choices[0].message.content or "{}"
            content = self._extract_json(content)

            try:
                action_data = json.loads(content)
            except json.JSONDecodeError:
                action_data = {
                    "thought": "无法解析模型输出",
                    "action": "finish",
                    "action_input": content[:500],
                }

            thought = action_data.get("thought", "")
            action = action_data.get("action", "finish")
            action_input = action_data.get("action_input", "")

            step_info = {
                "iteration": i + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input,
            }

            # 检查是否完成
            if action.lower() in ("finish", "done", "完成"):
                answer = action_input
                self.memory.add_assistant_message(answer)
                step_info["observation"] = "任务完成"
                steps.append(step_info)
                return {
                    "query": query,
                    "answer": answer,
                    "steps": steps,
                    "iterations": i + 1,
                    "history": self.memory.get_formatted_history(),
                }

            # 执行工具
            tool = self.tool_registry.get(action)
            if tool:
                observation = tool.run(action_input)
                self.memory.add_tool_message(action, observation)
                step_info["observation"] = observation
            else:
                observation = f"错误：未找到工具 '{action}'"
                step_info["observation"] = observation

            steps.append(step_info)

        # 达到最大迭代次数
        return {
            "query": query,
            "answer": "达到最大迭代次数，未能完成任务。",
            "steps": steps,
            "iterations": self.max_iterations,
            "history": self.memory.get_formatted_history(),
        }

    def run_stream(self, query: str) -> Gen[str, None, None]:
        """流式运行 Agent（逐步输出思考过程）"""
        self.memory.add_user_message(query)

        for i in range(self.max_iterations):
            history = self._build_history()
            tools_desc = self.tool_registry.get_tool_descriptions()

            prompt = self.REACT_PROMPT.format(
                tools_description=tools_desc,
                query=query,
                history=history,
            )

            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )

            content = response.choices[0].message.content or "{}"
            content = self._extract_json(content)

            try:
                action_data = json.loads(content)
            except json.JSONDecodeError:
                action_data = {
                    "thought": "无法解析",
                    "action": "finish",
                    "action_input": content[:500],
                }

            thought = action_data.get("thought", "")
            action = action_data.get("action", "finish")
            action_input = action_data.get("action_input", "")

            yield f"**思考 [{i+1}]**: {thought}\n\n"
            yield f"**行动**: {action}({action_input})\n\n"

            if action.lower() in ("finish", "done", "完成"):
                answer = action_input
                self.memory.add_assistant_message(answer)
                yield f"**完成**: {answer}\n\n"
                return

            tool = self.tool_registry.get(action)
            if tool:
                observation = tool.run(action_input)
                self.memory.add_tool_message(action, observation)
                yield f"**观察**: {observation[:300]}...\n\n---\n\n"
            else:
                yield f"**错误**: 未找到工具 '{action}'\n\n"

        yield "达到最大迭代次数。"

    def _build_history(self) -> str:
        """构建执行历史文本"""
        parts = []
        for m in self.memory.messages:
            if m.role == "user":
                parts.append(f"用户：{m.content}")
            elif m.role == "tool":
                tool_name = m.metadata.get("tool", "工具")
                parts.append(f"[{tool_name}] 返回：{m.content[:300]}")
        return "\n".join(parts)

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def reset(self) -> None:
        """重置 Agent 状态"""
        self.memory.clear()
        self.executor.execution_history.clear()
