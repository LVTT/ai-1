"""搜索工具

使用 DuckDuckGo 进行网络搜索（无需 API Key）。
"""

from typing import Optional


class SearchTool:
    """网络搜索工具"""

    name = "search"
    description = "使用搜索引擎查找网络信息。输入：搜索关键词"

    def run(self, query: str) -> str:
        """执行搜索

        Args:
            query: 搜索关键词
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "错误：未安装 duckduckgo-search，请执行 pip install duckduckgo-search"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return f"未找到与 '{query}' 相关的搜索结果。"

            lines = [f"搜索 '{query}' 的结果：\n"]
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r['title']}")
                lines.append(f"   {r['body'][:200]}...")
                lines.append(f"   链接：{r['href']}\n")

            return "\n".join(lines)

        except Exception as e:
            return f"搜索失败：{str(e)}"

    def __call__(self, query: str) -> str:
        return self.run(query)
