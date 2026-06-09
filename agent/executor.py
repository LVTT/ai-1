"""执行器模块

负责执行规划好的任务步骤，调用工具并收集结果。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from agent.tools import ToolRegistry


@dataclass
class ExecutionResult:
    """执行结果"""
    step_number: int
    description: str
    tool_used: Optional[str]
    tool_input: Optional[str]
    tool_output: str
    status: str  # "success", "error", "skipped"


class ToolExecutor:
    """工具执行器

    按步骤执行计划，调用相应工具。
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.execution_history: List[ExecutionResult] = []

    def execute_step(
        self,
        step: Dict[str, Any],
    ) -> ExecutionResult:
        """执行单个步骤"""
        step_num = step.get("step_number", 0)
        description = step.get("description", "")
        tool_name = step.get("tool")
        tool_input = step.get("tool_input", "")

        if not tool_name or tool_name.lower() in ("null", "none", ""):
            # 不需要工具，直接返回
            return ExecutionResult(
                step_number=step_num,
                description=description,
                tool_used=None,
                tool_input=None,
                tool_output="",
                status="skipped",
            )

        tool = self.tool_registry.get(tool_name)
        if not tool:
            return ExecutionResult(
                step_number=step_num,
                description=description,
                tool_used=tool_name,
                tool_input=tool_input,
                tool_output=f"错误：未找到工具 '{tool_name}'",
                status="error",
            )

        try:
            output = tool.run(tool_input)
            result = ExecutionResult(
                step_number=step_num,
                description=description,
                tool_used=tool_name,
                tool_input=tool_input,
                tool_output=output,
                status="success",
            )
        except Exception as e:
            result = ExecutionResult(
                step_number=step_num,
                description=description,
                tool_used=tool_name,
                tool_input=tool_input,
                tool_output=f"执行出错：{str(e)}",
                status="error",
            )

        self.execution_history.append(result)
        return result

    def execute_plan(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[ExecutionResult]:
        """执行完整的计划"""
        results = []
        for step in steps:
            result = self.execute_step(step)
            results.append(result)
        return results

    def get_execution_summary(self) -> str:
        """获取执行摘要"""
        lines = ["执行摘要："]
        for r in self.execution_history:
            status_icon = "✓" if r.status == "success" else "✗" if r.status == "error" else "-"
            lines.append(
                f"  {status_icon} 步骤 {r.step_number}: {r.description}")
            if r.tool_used:
                lines.append(f"    工具：{r.tool_used}({r.tool_input})")
                lines.append(f"    输出：{r.tool_output[:100]}...")
        return "\n".join(lines)

    def get_context_for_llm(self) -> str:
        """将执行历史格式化为 LLM 可用的上下文"""
        parts = []
        for r in self.execution_history:
            if r.tool_used:
                parts.append(
                    f"[步骤 {r.step_number}] 使用工具 '{r.tool_used}' "
                    f"(输入: {r.tool_input})\n"
                    f"结果：{r.tool_output}"
                )
            else:
                parts.append(f"[步骤 {r.step_number}] {r.description}")
        return "\n\n".join(parts)
