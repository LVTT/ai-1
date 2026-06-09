"""Prompt 模板加载器

从 YAML 文件加载 system_prompts 和 task_prompts，实现提示词与代码分离。
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# 获取 templates 目录路径（当前文件所在目录下的 templates/）
_TEMPLATES_DIR = Path(__file__).parent / "templates"

# 缓存加载的数据，避免重复读取文件
_task_prompts: Dict[str, Any] = {}
_system_prompts: Dict[str, Any] = {}


def _load_yaml(filename: str) -> Dict[str, Any]:
    """加载 YAML 文件并返回解析后的字典"""
    filepath = _TEMPLATES_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_task_prompt(name: str) -> str:
    """获取指定名称的任务 Prompt 模板

    Args:
        name: task_prompts.yaml 中的 key，如 "intent", "planning", "summarize"

    Returns:
        prompt 字符串，可调用 .format(...) 填入变量
    """
    global _task_prompts
    if not _task_prompts:
        _task_prompts = _load_yaml("task_prompts.yaml")
    return _task_prompts[name]["prompt"]


def get_system_prompt(name: str) -> str:
    """获取指定名称的系统 Prompt（角色设定）

    Args:
        name: system_prompts.yaml 中的 key，如 "assistant", "coder", "planner"

    Returns:
        prompt 字符串，用于 system 消息
    """
    global _system_prompts
    if not _system_prompts:
        _system_prompts = _load_yaml("system_prompts.yaml")
    return _system_prompts[name]["prompt"]
