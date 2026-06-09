"""任务规划模块

负责将用户请求拆解为可执行的任务步骤。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL


@dataclass
class TaskPlan:
    """任务计划"""
    steps: List[Dict[str, Any]]
    reasoning: str


class TaskPlanner:
    """任务规划器

    将复杂请求分解为多个可执行步骤。
    """

    PLANNING_PROMPT = """你是一个任务规划专家。请将用户的请求分解为具体的执行步骤。

可用的工具：
{tools_description}

请按以下 JSON 格式输出计划：
{{
  "reasoning": "对任务的分析和规划思路",
  "steps": [
    {{
      "step_number": 1,
      "description": "步骤描述",
      "tool": "工具名称（如不需要工具则填 null）",
      "tool_input": "工具的输入参数"
    }}
  ]
}}

注意：
1. 每个步骤应该明确、可执行
2. 优先使用工具获取实时信息
3. 如果任务简单，可以只有一步
4. 最后一步应该是综合所有信息给出最终回答

用户请求：{query}

请输出计划（只输出 JSON，不要其他内容）："""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_LLM_MODEL
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

    def plan(
        self,
        query: str,
        tools_description: str,
    ) -> TaskPlan:
        """为查询生成执行计划"""
        prompt = self.PLANNING_PROMPT.format(
            tools_description=tools_description,
            query=query,
        )

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )

        content = response.choices[0].message.content or "{}"

        # 清理 JSON
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            plan_data = json.loads(content)
        except json.JSONDecodeError:
            # 降级：返回单步计划
            plan_data = {
                "reasoning": "无法解析计划，采用单步执行",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "直接回答用户问题",
                        "tool": None,
                        "tool_input": None,
                    }
                ],
            }

        return TaskPlan(
            steps=plan_data.get("steps", []),
            reasoning=plan_data.get("reasoning", ""),
        )

    def simple_plan(self, query: str, available_tools: List[str]) -> List[str]:
        """简单规划：只返回建议使用的工具列表"""
        plan = self.plan(query, "\n".join(available_tools))
        tools_used = [
            step.get("tool") for step in plan.steps
            if step.get("tool")
        ]
        return tools_used
