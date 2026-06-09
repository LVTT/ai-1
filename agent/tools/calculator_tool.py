"""计算器工具

支持数学表达式计算。
"""

import re


class CalculatorTool:
    """数学计算工具"""

    name = "calculator"
    description = "计算数学表达式。输入：数学表达式（如 2+2, sqrt(16), 3**2）"

    def run(self, expression: str) -> str:
        """执行计算

        Args:
            expression: 数学表达式
        """
        # 清理输入
        expression = expression.strip()

        # 安全检查：只允许数字、运算符、括号和数学函数
        allowed_pattern = r'^[\d\+\-\*\/\(\)\.\^\%\s\,]+$'
        if not re.match(allowed_pattern, expression):
            # 尝试提取表达式
            expression = self._extract_expression(expression)
            if not expression:
                return "错误：输入包含不安全的字符，请输入纯数学表达式。"

        try:
            import numexpr as ne
            result = ne.evaluate(expression)
            return f"计算结果：{expression} = {result}"
        except ImportError:
            # 降级到 eval（仅基础运算）
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                return f"计算结果：{expression} = {result}"
            except Exception as e:
                return f"计算失败：{str(e)}。请安装 numexpr 以获得更好的支持：pip install numexpr"
        except Exception as e:
            return f"计算失败：{str(e)}"

    def _extract_expression(self, text: str) -> str:
        """从文本中提取数学表达式"""
        # 匹配常见的数学表达式模式
        patterns = [
            r'[\d\+\-\*\/\(\)\.\^\%\s]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return ""

    def __call__(self, expression: str) -> str:
        return self.run(expression)
