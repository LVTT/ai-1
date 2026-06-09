"""Prompt 进阶技巧

包含 Few-shot、CoT、Self-Consistency、ToT、ReAct 等进阶 Prompt 工程技巧。
"""

from typing import List, Dict, Any


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
    base = (
        f"问题：{user_input}\n\n"
        "请逐步思考这个问题，展示你的推理过程，最后给出答案。\n"
        "格式要求：\n"
        "推理过程：\n"
        "1. ...\n"
        "2. ...\n"
        "...\n"
        "最终答案：..."
    )
    if reasoning_instruction:
        base = f"{reasoning_instruction}\n\n{base}"
    return base


def self_consistency_prompt(user_input: str, num_paths: int = 3) -> str:
    """Self-Consistency Prompt：让模型生成多条推理路径并选择最一致的答案

    使用方式：
        1. 调用此 Prompt 生成回答
        2. 多次采样（temperature > 0）
        3. 对多次回答进行投票，选择最常见的答案
    """
    return (
        f"问题：{user_input}\n\n"
        f"请从 {num_paths} 个不同的角度思考这个问题，"
        "分别展示推理过程，然后综合所有角度给出最可靠的答案。\n\n"
        "角度 1：\n"
        "推理过程：...\n"
        "结论：...\n\n"
        "角度 2：\n"
        "推理过程：...\n"
        "结论：...\n\n"
        "...\n\n"
        "综合判断："
    )


def tree_of_thoughts_prompt(user_input: str, num_branches: int = 3, depth: int = 2) -> str:
    """Tree-of-Thoughts (ToT) Prompt：树状思考，探索多种可能性

    核心思想：在每个思考步骤生成多个候选，评估后继续深入最有希望的节点
    """
    return (
        f"问题：{user_input}\n\n"
        "请使用树状思考方式解决这个问题。\n"
        f"在每一步生成 {num_branches} 个可能的思考方向，"
        f"评估每个方向的可行性，然后选择最有希望的方向深入（最多 {depth} 层）。\n\n"
        "思考树结构：\n"
        "步骤 1：\n"
        "- 方向 A：...（评估：优/良/差）\n"
        "- 方向 B：...（评估：优/良/差）\n"
        "- 方向 C：...（评估：优/良/差）\n"
        "选择：方向 X\n\n"
        "步骤 2：\n"
        "...\n\n"
        "最终结论："
    )


def react_prompt_template() -> str:
    """ReAct Prompt Template：推理与行动交替进行

    这是 Agent 的基础 Prompt 模板，结合思考（Thought）、行动（Action）、观察（Observation）
    """
    return """你是一个智能助手，可以使用工具来解决问题。请按照以下格式思考并行动：

思考过程：分析当前情况，决定下一步行动
行动：使用工具（格式：工具名称[参数]）
观察：工具返回的结果
...（重复思考-行动-观察循环）
最终答案：给出最终回答

你可以使用的工具：
{tools_description}

当前问题：{question}

请开始思考与行动：
思考："""


def automatic_prompt_engineering_prompt(task_description: str, initial_prompt: str = "") -> str:
    """APE (Automatic Prompt Engineering)：让模型自己优化 Prompt"""
    return (
        f"任务描述：{task_description}\n\n"
        f"初始 Prompt：{initial_prompt or '（暂无）'}\n\n"
        "请执行以下步骤来优化这个 Prompt：\n"
        "1. 分析任务的核心需求\n"
        "2. 指出当前 Prompt 的不足\n"
        "3. 提出 3 个改进版本\n"
        "4. 解释每个版本的优劣\n"
        "5. 推荐最佳版本并说明理由"
    )


def meta_prompting(user_input: str) -> str:
    """Meta Prompting：让模型先生成 Prompt，再用 Prompt 回答问题"""
    return (
        f"用户原始请求：{user_input}\n\n"
        "第一步：请为这个请求设计一个最优的 Prompt 模板。\n"
        "考虑因素：角色设定、输出格式、约束条件、示例等。\n\n"
        "第二步：使用你设计的 Prompt 来回答用户的请求。\n\n"
        "设计的 Prompt：\n"
        "...\n\n"
        "基于该 Prompt 的回答："
    )


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
