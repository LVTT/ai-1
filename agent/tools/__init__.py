"""Agent 工具模块

定义各种可调用工具及工具注册中心。
"""

from .search_tool import SearchTool
from .calculator_tool import CalculatorTool
from .weather_tool import WeatherTool


class ToolRegistry:
    """工具注册中心

    管理所有可用工具，支持动态注册和查找。
    """

    def __init__(self):
        self._tools: dict = {}

    def register(self, tool) -> "ToolRegistry":
        """注册工具"""
        self._tools[tool.name] = tool
        return self

    def get(self, name: str):
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list:
        """列出所有工具"""
        return list(self._tools.values())

    def get_tool_descriptions(self) -> str:
        """获取所有工具的描述文本（用于 Prompt）"""
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)

    def __contains__(self, name: str) -> bool:
        return name in self._tools


def get_default_tools() -> ToolRegistry:
    """获取默认工具集"""
    registry = ToolRegistry()
    registry.register(SearchTool())
    registry.register(CalculatorTool())
    registry.register(WeatherTool())
    return registry


__all__ = [
    "SearchTool",
    "CalculatorTool",
    "WeatherTool",
    "ToolRegistry",
    "get_default_tools",
]
