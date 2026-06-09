"""Prompt 基础技巧

包含最基本的 Prompt 编写方法，适合初学者理解和练习。
"""

from typing import Optional

from prompts.templates import get_task_prompt


def basic_prompt(user_input: str) -> str:
    """最基础的 Prompt：直接传递用户输入"""
    return user_input


def role_prompt(user_input: str, role: str = "有帮助的助手") -> str:
    """角色设定 Prompt：给模型一个明确的角色

    示例：
        role_prompt("解释量子力学", "物理学教授")
    """
    template = get_task_prompt("role")
    return template.format(role=role, user_input=user_input)


def instruction_prompt(user_input: str, instruction: str) -> str:
    """指令式 Prompt：明确告诉模型要做什么

    示例：
        instruction_prompt("气候变化", "用三句话概括以下内容的核心观点")
    """
    template = get_task_prompt("instruction")
    return template.format(instruction=instruction, user_input=user_input)


def context_prompt(user_input: str, context: str) -> str:
    """上下文 Prompt：提供背景信息后再提问

    示例：
        context_prompt("我应该怎么做？", "我是一个刚开始学Python的程序员")
    """
    template = get_task_prompt("context")
    return template.format(context=context, user_input=user_input)


def format_prompt(user_input: str, output_format: str) -> str:
    """格式约束 Prompt：指定输出格式

    示例：
        format_prompt("苹果、香蕉、橙子", "JSON格式，包含名称和价格字段")
    """
    template = get_task_prompt("format")
    return template.format(user_input=user_input, output_format=output_format)


def step_by_step_prompt(user_input: str) -> str:
    """分步思考 Prompt：引导模型逐步思考（简单版 CoT）"""
    template = get_task_prompt("step_by_step")
    return template.format(user_input=user_input)


def constraint_prompt(user_input: str, constraints: list[str]) -> str:
    """约束条件 Prompt：添加各种限制条件"""
    constraints_text = "\n".join(f"- {c}" for c in constraints)
    template = get_task_prompt("constraint")
    return template.format(user_input=user_input, constraints_text=constraints_text)


def persona_prompt(user_input: str, persona: dict) -> str:
    """详细人设 Prompt：构建完整的人物设定

    示例：
        persona = {
            "name": "李博士",
            "职业": "数据科学家",
            "专长": ["机器学习", "统计学"],
            "语气": "专业但平易近人",
            "回答风格": "喜欢用类比解释复杂概念"
        }
    """
    persona_lines = []
    for key, value in persona.items():
        if isinstance(value, list):
            value = ", ".join(value)
        persona_lines.append(f"- {key}：{value}")
    persona_text = "\n".join(persona_lines)

    template = get_task_prompt("persona")
    return template.format(persona_text=persona_text, user_input=user_input)


def auto_optimize_prompt(user_input: str) -> str:
    """智能优化 Prompt：自动分析用户输入并生成最佳 Prompt

    调用 LLM 识别最适合的技巧组合，直接返回优化后的完整 Prompt。
    """
    from openai import OpenAI
    from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL

    template = get_task_prompt("optimize_prompt")
    prompt = template.format(user_input=user_input)

    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model=DEFAULT_LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content or user_input
