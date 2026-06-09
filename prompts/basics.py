"""Prompt 基础技巧

包含最基本的 Prompt 编写方法，适合初学者理解和练习。
"""

from typing import Optional


def basic_prompt(user_input: str) -> str:
    """最基础的 Prompt：直接传递用户输入"""
    return user_input


def role_prompt(user_input: str, role: str = "有帮助的助手") -> str:
    """角色设定 Prompt：给模型一个明确的角色

    示例：
        role_prompt("解释量子力学", "物理学教授")
    """
    return f"你是一位{role}。请回答以下问题：\n\n{user_input}"


def instruction_prompt(user_input: str, instruction: str) -> str:
    """指令式 Prompt：明确告诉模型要做什么

    示例：
        instruction_prompt("气候变化", "用三句话概括以下内容的核心观点")
    """
    return f"{instruction}：\n\n{user_input}"


def context_prompt(user_input: str, context: str) -> str:
    """上下文 Prompt：提供背景信息后再提问

    示例：
        context_prompt("我应该怎么做？", "我是一个刚开始学Python的程序员")
    """
    return f"背景信息：\n{context}\n\n问题：\n{user_input}"


def format_prompt(user_input: str, output_format: str) -> str:
    """格式约束 Prompt：指定输出格式

    示例：
        format_prompt("苹果、香蕉、橙子", "JSON格式，包含名称和价格字段")
    """
    return f"{user_input}\n\n请按照以下格式输出：{output_format}"


def step_by_step_prompt(user_input: str) -> str:
    """分步思考 Prompt：引导模型逐步思考（简单版 CoT）"""
    return (
        f"{user_input}\n\n"
        "请按照以下步骤思考并回答：\n"
        "1. 分析问题关键点\n"
        "2. 逐步推导解决方案\n"
        "3. 给出最终答案\n"
        "4. 验证答案的合理性"
    )


def constraint_prompt(user_input: str, constraints: list[str]) -> str:
    """约束条件 Prompt：添加各种限制条件"""
    constraints_text = "\n".join(f"- {c}" for c in constraints)
    return (
        f"{user_input}\n\n"
        f"请遵守以下约束条件：\n{constraints_text}"
    )


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

    return (
        f"请扮演以下角色：\n{persona_text}\n\n"
        f"用户问题：\n{user_input}"
    )
