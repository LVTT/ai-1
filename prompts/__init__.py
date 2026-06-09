"""Prompt 工程模块

包含基础 Prompt 技巧、进阶技巧（CoT、Few-shot 等）以及调试工具。
"""

from .basics import (
    basic_prompt,
    role_prompt,
    instruction_prompt,
    context_prompt,
    format_prompt,
)
from .advanced import (
    few_shot_prompt,
    chain_of_thought_prompt,
    self_consistency_prompt,
    tree_of_thoughts_prompt,
    react_prompt_template,
)
from .debug_tools import (
    PromptDebugger,
    compare_prompts,
    evaluate_prompt,
)
from .templates import (
    get_task_prompt,
    get_system_prompt,
)

__all__ = [
    # 基础
    "basic_prompt",
    "role_prompt",
    "instruction_prompt",
    "context_prompt",
    "format_prompt",
    # 进阶
    "few_shot_prompt",
    "chain_of_thought_prompt",
    "self_consistency_prompt",
    "tree_of_thoughts_prompt",
    "react_prompt_template",
    # 调试
    "PromptDebugger",
    "compare_prompts",
    "evaluate_prompt",
    # YAML 模板加载
    "get_task_prompt",
    "get_system_prompt",
]
