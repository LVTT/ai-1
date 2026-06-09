"""Prompt 进阶技巧

包含 Few-shot、CoT、Self-Consistency、ToT、ReAct 等进阶 Prompt 工程技巧。
"""

from typing import List, Dict, Any

from prompts.templates import get_task_prompt


def few_shot_prompt(user_input: str, examples: List[Dict[str, str]], instruction: str = "") -> str:
    """Few-shot Prompt：通过示例教模型如何回答

    示例：
        examples = [
            {"input": "今天天气真好", "output": "正面"},
            {"input": "这部电影太烂了", "output": "负面"},
        ]
        few_shot_prompt("这个产品非常好用", examples, "判断情感倾向")
    """
    lines = []
    if instruction:
        lines.append(f"任务说明：{instruction}")
        lines.append("")

    lines.append("以下是一些示例：")
    for i, ex in enumerate(examples, 1):
        lines.append(f"\n示例 {i}：")
        lines.append(f"输入：{ex['input']}")
        lines.append(f"输出：{ex['output']}")

    lines.append("\n现在请回答：")
    lines.append(f"输入：{user_input}")
    lines.append("输出：")

    return "\n".join(lines)


def chain_of_thought_prompt(user_input: str, reasoning_instruction: str = "") -> str:
    """Chain-of-Thought (CoT) Prompt：引导模型展示推理过程

    核心思想：让模型"先思考，再回答"
    """
    reasoning_instruction_section = f"{reasoning_instruction}\n\n" if reasoning_instruction else ""
    template = get_task_prompt("chain_of_thought")
    return template.format(
        reasoning_instruction_section=reasoning_instruction_section,
        user_input=user_input,
    )


def self_consistency_prompt(user_input: str, num_paths: int = 3) -> str:
    """Self-Consistency Prompt：让模型生成多条推理路径并选择最一致的答案"""
    template = get_task_prompt("self_consistency")
    return template.format(user_input=user_input, num_paths=num_paths)


def tree_of_thoughts_prompt(user_input: str, num_branches: int = 3, depth: int = 2) -> str:
    """Tree-of-Thoughts (ToT) Prompt：树状思考，探索多种可能性

    核心思想：在每个思考步骤生成多个候选，评估后继续深入最有希望的节点
    """
    template = get_task_prompt("tree_of_thoughts")
    return template.format(
        user_input=user_input,
        num_branches=num_branches,
        depth=depth,
    )


def react_prompt_template() -> str:
    """ReAct Prompt Template：推理与行动交替进行

    这是 Agent 的基础 Prompt 模板，结合思考（Thought）、行动（Action）、观察（Observation）
    """
    return get_task_prompt("react")


def automatic_prompt_engineering_prompt(task_description: str, initial_prompt: str = "") -> str:
    """APE (Automatic Prompt Engineering)：让模型自己优化 Prompt"""
    template = get_task_prompt("automatic_prompt_engineering")
    return template.format(
        task_description=task_description,
        initial_prompt=initial_prompt or "（暂无）",
    )


def meta_prompting(user_input: str) -> str:
    """Meta Prompting：让模型先生成 Prompt，再用 Prompt 回答问题"""
    template = get_task_prompt("meta_prompting")
    return template.format(user_input=user_input)


def prompt_chaining_prompt(steps: List[str], user_input: str) -> List[str]:
    """Prompt Chaining：将复杂任务拆分为多个子 Prompt

    返回一个 Prompt 列表，每个对应一个子任务
    """
    prompts = []
    for i, step in enumerate(steps):
        if i == 0:
            prompts.append(
                f"步骤 {i+1}/{len(steps)}：{step}\n\n"
                f"输入：{user_input}\n"
                f"请完成此步骤，输出结果："
            )
        else:
            prompts.append(
                f"步骤 {i+1}/{len(steps)}：{step}\n\n"
                f"上一步的输出：{{previous_output}}\n"
                f"请基于上一步结果完成此步骤："
            )
    return prompts
