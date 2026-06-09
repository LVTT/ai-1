"""Prompt 调试工具

用于评估、比较和优化 Prompt 的工具集。
"""

import time
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class PromptResult:
    """Prompt 执行结果"""
    prompt: str
    response: str
    latency_ms: float
    token_count: Optional[int] = None
    score: Optional[float] = None


@dataclass
class PromptEvaluation:
    """Prompt 评估结果"""
    prompt: str
    results: List[PromptResult]
    avg_latency: float
    avg_score: float
    consistency: float  # 多次输出的一致性
    pass_rate: float    # 测试用例通过率


class PromptDebugger:
    """Prompt 调试器

    用法：
        debugger = PromptDebugger(llm_callback)
        debugger.add_test_case("输入1", "期望输出1")
        result = debugger.evaluate("你的 Prompt")
    """

    def __init__(self, llm_callback: Callable[[str], str]):
        """
        Args:
            llm_callback: 接收 prompt 字符串，返回模型输出的函数
        """
        self.llm_callback = llm_callback
        self.test_cases: List[Dict[str, Any]] = []

    def add_test_case(
        self,
        input_text: str,
        expected_output: Optional[str] = None,
        evaluation_criteria: Optional[str] = None,
    ) -> "PromptDebugger":
        """添加测试用例"""
        self.test_cases.append({
            "input": input_text,
            "expected": expected_output,
            "criteria": evaluation_criteria,
        })
        return self

    def run_single(
        self,
        prompt: str,
        input_text: str,
        num_samples: int = 1,
    ) -> List[PromptResult]:
        """对单个输入运行多次采样"""
        results = []
        full_prompt = f"{prompt}\n\n输入：{input_text}\n输出："

        for _ in range(num_samples):
            start = time.time()
            response = self.llm_callback(full_prompt)
            latency = (time.time() - start) * 1000

            results.append(PromptResult(
                prompt=full_prompt,
                response=response,
                latency_ms=latency,
            ))

        return results

    def evaluate(
        self,
        prompt: str,
        num_samples: int = 1,
    ) -> List[Dict[str, Any]]:
        """评估 Prompt 在所有测试用例上的表现"""
        all_results = []

        for case in self.test_cases:
            results = self.run_single(prompt, case["input"], num_samples)

            # 简单评估：检查期望输出是否包含在响应中
            scores = []
            for r in results:
                if case.get("expected"):
                    score = 1.0 if case["expected"] in r.response else 0.0
                else:
                    score = 0.5  # 无明确期望时给中性分
                r.score = score
                scores.append(score)

            all_results.append({
                "input": case["input"],
                "expected": case.get("expected"),
                "results": results,
                "avg_score": sum(scores) / len(scores),
            })

        return all_results

    def compare_prompts(
        self,
        prompts: List[str],
        num_samples: int = 1,
    ) -> Dict[str, Any]:
        """比较多个 Prompt 的效果"""
        comparison = {}
        for i, prompt in enumerate(prompts):
            name = f"Prompt_{i+1}"
            results = self.evaluate(prompt, num_samples)
            avg_score = sum(r["avg_score"] for r in results) / len(results)
            comparison[name] = {
                "prompt": prompt,
                "results": results,
                "overall_score": avg_score,
            }
        return comparison


def compare_prompts(
    prompts: List[str],
    test_inputs: List[str],
    llm_callback: Callable[[str], str],
) -> Dict[str, Any]:
    """快速比较多个 Prompt 的效果

    Returns:
        包含每个 Prompt 在各输入上的表现对比
    """
    debugger = PromptDebugger(llm_callback)
    for inp in test_inputs:
        debugger.add_test_case(inp)

    return debugger.compare_prompts(prompts)


def evaluate_prompt(
    prompt: str,
    test_cases: List[Dict[str, Any]],
    llm_callback: Callable[[str], str],
) -> Dict[str, Any]:
    """评估单个 Prompt 的效果"""
    debugger = PromptDebugger(llm_callback)
    for case in test_cases:
        debugger.add_test_case(
            case["input"],
            case.get("expected"),
            case.get("criteria"),
        )
    return {
        "prompt": prompt,
        "case_results": debugger.evaluate(prompt),
    }


def analyze_prompt_weaknesses(prompt: str, responses: List[str]) -> List[str]:
    """分析 Prompt 的弱点

    基于多次响应，识别可能的问题：
    - 输出不一致
    - 回答不完整
    - 格式混乱等
    """
    weaknesses = []

    if len(responses) < 2:
        weaknesses.append("样本数不足，无法进行一致性分析")
        return weaknesses

    # 检查长度差异
    lengths = [len(r) for r in responses]
    avg_len = sum(lengths) / len(lengths)
    max_diff = max(lengths) - min(lengths)
    if max_diff > avg_len * 0.5:
        weaknesses.append(f"输出长度波动大（差异 {max_diff} 字符），Prompt 可能需要更明确的格式约束")

    # 检查是否有空回答
    if any(len(r.strip()) < 10 for r in responses):
        weaknesses.append("存在过短/空回答，Prompt 可能需要更清晰的指令")

    return weaknesses
