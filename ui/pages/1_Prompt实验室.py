import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import check_api_key
from prompts.basics import (
    basic_prompt, role_prompt, instruction_prompt, context_prompt,
    format_prompt, step_by_step_prompt, constraint_prompt, persona_prompt,
)
from prompts.advanced import (
    few_shot_prompt, chain_of_thought_prompt, self_consistency_prompt,
    tree_of_thoughts_prompt, react_prompt_template, automatic_prompt_engineering_prompt,
)
from ui.components.common import api_key_warning, code_showcase

st.set_page_config(page_title="Prompt 实验室", page_icon="📝", layout="wide")

st.title("📝 Prompt 工程实验室")

api_key_warning()

st.markdown("""
Prompt 工程是通过优化输入提示来提升大语言模型输出质量的技术。
本实验室包含基础技巧和进阶技巧，你可以实时输入内容并查看生成的 Prompt。
""")

# 侧边栏选择技巧类型
with st.sidebar:
    st.header("技巧选择")
    technique_category = st.radio(
        "选择类别",
        ["基础技巧", "进阶技巧"],
    )

if technique_category == "基础技巧":
    st.header("基础 Prompt 技巧")

    technique = st.selectbox(
        "选择技巧",
        [
            "直接提问 (Basic)",
            "角色设定 (Role)",
            "指令明确 (Instruction)",
            "提供上下文 (Context)",
            "格式约束 (Format)",
            "分步思考 (Step-by-Step)",
            "约束条件 (Constraint)",
            "详细人设 (Persona)",
        ],
    )

    user_input = st.text_area("输入你的问题/内容", "解释什么是机器学习", height=100)

    if technique == "直接提问 (Basic)":
        prompt = basic_prompt(user_input)
        code_showcase("代码", "from prompts.basics import basic_prompt\n\nprompt = basic_prompt(user_input)")

    elif technique == "角色设定 (Role)":
        role = st.text_input("角色", "机器学习专家")
        prompt = role_prompt(user_input, role)
        code_showcase("代码", f'prompt = role_prompt(user_input, "{role}")')

    elif technique == "指令明确 (Instruction)":
        instruction = st.text_input("指令", "用三句话概括")
        prompt = instruction_prompt(user_input, instruction)
        code_showcase("代码", f'prompt = instruction_prompt(user_input, "{instruction}")')

    elif technique == "提供上下文 (Context)":
        context = st.text_area("上下文", "我正在准备一场关于 AI 的演讲，听众是非技术人员")
        prompt = context_prompt(user_input, context)
        code_showcase("代码", "prompt = context_prompt(user_input, context)")

    elif technique == "格式约束 (Format)":
        fmt = st.text_input("格式要求", "Markdown 格式，使用列表和加粗")
        prompt = format_prompt(user_input, fmt)
        code_showcase("代码", f'prompt = format_prompt(user_input, "{fmt}")')

    elif technique == "分步思考 (Step-by-Step)":
        prompt = step_by_step_prompt(user_input)
        code_showcase("代码", "prompt = step_by_step_prompt(user_input)")

    elif technique == "约束条件 (Constraint)":
        constraints_input = st.text_area("约束条件（每行一个）", "回答不超过100字\n使用中文\n避免专业术语")
        constraints = [c.strip() for c in constraints_input.split("\n") if c.strip()]
        prompt = constraint_prompt(user_input, constraints)
        code_showcase("代码", "prompt = constraint_prompt(user_input, constraints)")

    elif technique == "详细人设 (Persona)":
        st.info("使用预设人设模板")
        persona = {
            "name": "李老师",
            "职业": "大学教授",
            "教学风格": "喜欢用生活中的类比解释复杂概念",
            "语气": "亲切、耐心",
            "回答结构": "先给出直观理解，再展开细节",
        }
        prompt = persona_prompt(user_input, persona)
        code_showcase("代码", "persona = {\"name\": \"李老师\", \"职业\": \"大学教授\", ...}\nprompt = persona_prompt(user_input, persona)")

    st.divider()
    st.subheader("生成的 Prompt")
    st.code(prompt, language="text")

    if st.button("🚀 调用 LLM 查看效果") and check_api_key():
        with st.spinner("正在生成..."):
            try:
                from openai import OpenAI
                from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL
                client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
                response = client.chat.completions.create(
                    model=DEFAULT_LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                st.markdown("**LLM 回答：**")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"调用失败：{e}")

else:
    st.header("进阶 Prompt 技巧")

    technique = st.selectbox(
        "选择技巧",
        [
            "Few-Shot 示例学习",
            "Chain-of-Thought 思维链",
            "Self-Consistency 自一致性",
            "Tree-of-Thoughts 思维树",
            "ReAct 模板",
            "自动 Prompt 工程 (APE)",
        ],
    )

    if technique == "Few-Shot 示例学习":
        st.markdown("通过提供输入-输出示例，教会模型如何回答。")
        user_input = st.text_area("测试输入", "这家餐厅的服务太糟糕了")

        examples = [
            {"input": "今天天气真好，适合出游", "output": "正面"},
            {"input": "这部电影太烂了，浪费钱", "output": "负面"},
            {"input": "产品质量一般，无功无过", "output": "中性"},
        ]
        instruction = "判断以下句子的情感倾向（正面/负面/中性）"
        prompt = few_shot_prompt(user_input, examples, instruction)

        with st.expander("查看示例数据"):
            st.json(examples)

        code_showcase("代码", "examples = [{\"input\": \"...\", \"output\": \"...\"}]\nprompt = few_shot_prompt(user_input, examples, instruction)")

    elif technique == "Chain-of-Thought 思维链":
        st.markdown("引导模型展示推理过程，而非直接给出答案。")
        user_input = st.text_area("问题", "一个农场有鸡和兔共35只，脚共94只。鸡和兔各有多少只？")
        prompt = chain_of_thought_prompt(user_input)
        code_showcase("代码", "prompt = chain_of_thought_prompt(user_input)")

    elif technique == "Self-Consistency 自一致性":
        st.markdown("让模型从多个角度思考，选择最一致的答案。")
        user_input = st.text_area("问题", "如何提高代码的可维护性？")
        num_paths = st.slider("思考角度数", 2, 5, 3)
        prompt = self_consistency_prompt(user_input, num_paths)
        code_showcase("代码", f"prompt = self_consistency_prompt(user_input, {num_paths})")

    elif technique == "Tree-of-Thoughts 思维树":
        st.markdown("在每个思考步骤探索多种可能性，像树一样分支。")
        user_input = st.text_area("问题", "设计一个高性能的Web API")
        prompt = tree_of_thoughts_prompt(user_input, num_branches=3, depth=2)
        code_showcase("代码", "prompt = tree_of_thoughts_prompt(user_input, num_branches=3, depth=2)")

    elif technique == "ReAct 模板":
        st.markdown("ReAct = Reasoning + Acting，让模型交替进行思考和行动。")
        prompt = react_prompt_template()
        st.info("这是一个模板函数，需要传入 tools_description 和 question")
        code_showcase("代码", 'prompt = react_prompt_template()\nformatted = prompt.format(tools_description="...", question="...")')
        # 展示格式化后的样子
        tools_desc = "- search: 搜索网络信息\n- calculator: 计算数学表达式"
        question = "2024年诺贝尔奖得主是谁？"
        formatted = prompt.format(tools_description=tools_desc, question=question)
        prompt = formatted

    elif technique == "自动 Prompt 工程 (APE)":
        st.markdown("让模型自己分析和优化 Prompt。")
        task = st.text_area("任务描述", "从文本中提取人名、地点和时间")
        initial = st.text_area("初始 Prompt（可选）", "")
        prompt = automatic_prompt_engineering_prompt(task, initial)
        code_showcase("代码", "prompt = automatic_prompt_engineering_prompt(task_description, initial_prompt)")

    st.divider()
    st.subheader("生成的 Prompt")
    st.code(prompt, language="text")

    if st.button("🚀 调用 LLM 查看效果") and check_api_key():
        with st.spinner("正在生成..."):
            try:
                from openai import OpenAI
                from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL
                client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
                response = client.chat.completions.create(
                    model=DEFAULT_LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                st.markdown("**LLM 回答：**")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"调用失败：{e}")
