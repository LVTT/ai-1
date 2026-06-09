"""记忆模块

管理对话历史和上下文记忆。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Message:
    """对话消息"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """对话记忆管理器

    支持滑动窗口和摘要压缩两种模式。
    """

    def __init__(
        self,
        max_messages: int = 20,
        enable_summarization: bool = False,
    ):
        self.messages: deque = deque(maxlen=max_messages)
        self.max_messages = max_messages
        self.enable_summarization = enable_summarization
        self.summary: str = ""

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """添加消息"""
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata or {},
        ))

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.add_message("assistant", content)

    def add_tool_message(self, tool_name: str, output: str) -> None:
        """添加工具调用结果"""
        self.add_message("tool", output, metadata={"tool": tool_name})

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """获取消息列表（OpenAI 格式）"""
        msgs = list(self.messages)
        if limit:
            msgs = msgs[-limit:]
        return [{"role": m.role, "content": m.content} for m in msgs]

    def get_formatted_history(self) -> str:
        """获取格式化的对话历史"""
        lines = []
        for m in self.messages:
            if m.role == "user":
                lines.append(f"用户：{m.content}")
            elif m.role == "assistant":
                lines.append(f"助手：{m.content}")
            elif m.role == "tool":
                tool = m.metadata.get("tool", "工具")
                lines.append(f"[{tool}]：{m.content[:200]}...")
        return "\n".join(lines)

    def clear(self) -> None:
        """清空记忆"""
        self.messages.clear()
        self.summary = ""

    def is_empty(self) -> bool:
        """是否为空"""
        return len(self.messages) == 0

    def get_context_window(self, max_tokens: int = 4000) -> List[Dict[str, str]]:
        """获取上下文窗口（简单估算 token 数）"""
        # 粗略估算：1 个汉字约 1.5 tokens
        msgs = []
        total_chars = 0
        max_chars = int(max_tokens / 1.5)

        for m in reversed(self.messages):
            msg_chars = len(m.content)
            if total_chars + msg_chars > max_chars and msgs:
                break
            msgs.insert(0, {"role": m.role, "content": m.content})
            total_chars += msg_chars

        return msgs


class WorkingMemory:
    """工作记忆

    存储当前任务执行过程中的临时信息。
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """设置键值"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取值"""
        return self.data.get(key, default)

    def clear(self) -> None:
        """清空"""
        self.data.clear()
