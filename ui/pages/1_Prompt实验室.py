import streamlit as st  # 导入 Streamlit 库，用于构建 Web 界面

from config.settings import check_api_key  # 从配置模块导入 API Key 检查函数
from prompts.basics import (  # 从基础 Prompt 模块导入各类基础技巧函数
    basic_prompt, role_prompt, instruction_prompt, context_prompt,  # 基础技巧：直接提问、角色设定、指令、上下文
    # 基础技巧：格式约束、分步思考、约束条件、人设
    format_prompt, step_by_step_prompt, constraint_prompt, persona_prompt,
    auto_optimize_prompt,  # 智能优化：自动分析用户输入并生成最佳 Prompt
)
from prompts.advanced import (  # 从进阶 Prompt 模块导入各类进阶技巧函数
    # 进阶技巧：Few-Shot、思维链、自一致性
    few_shot_prompt, chain_of_thought_prompt, self_consistency_prompt,
    # 进阶技巧：思维树、ReAct、自动 Prompt 工程
    tree_of_thoughts_prompt, react_prompt_template, automatic_prompt_engineering_prompt,
)
# 从公共组件导入 API Key 警告框和代码展示组件
from ui.components.common import api_key_warning, code_showcase

st.set_page_config(page_title="Prompt 实验室", page_icon="📝",
                   layout="wide")  # 设置页面标题、图标和布局为宽屏模式

st.title("📝 Prompt 工程实验室")  # 页面主标题

api_key_warning()  # 显示 API Key 配置警告（如果未配置则提示用户）

st.markdown("""
Prompt 工程是通过优化输入提示来提升大语言模型输出质量的技术。
本实验室包含基础技巧和进阶技巧，你可以实时输入内容并查看生成的 Prompt。
""")  # 页面顶部说明文字，介绍 Prompt 工程的作用

# 侧边栏选择技巧类型
with st.sidebar:  # 进入侧边栏上下文，以下组件显示在左侧边栏
    st.header("技巧选择")  # 侧边栏小标题
    technique_category = st.radio(  # 单选按钮组件，让用户选择三大类模式
        "选择类别",  # 单选框标签
        ["基础技巧", "进阶技巧", "🤖 智能优化"],  # 三个选项：基础、进阶、全自动智能优化
    )

if technique_category == "基础技巧":  # 如果用户选择了"基础技巧"
    st.header("基础 Prompt 技巧")  # 显示基础技巧区域标题

    technique = st.selectbox(  # 下拉选择框，让用户选择具体的基础技巧
        "选择技巧",  # 下拉框标签
        [  # 8 个基础技巧选项
            "直接提问 (Basic)",  # 不做任何加工，直接传递用户输入
            "角色设定 (Role)",  # 给模型设定一个角色身份
            "指令明确 (Instruction)",  # 明确告诉模型要执行什么任务
            "提供上下文 (Context)",  # 补充背景信息帮助模型理解
            "格式约束 (Format)",  # 要求模型按特定格式输出
            "分步思考 (Step-by-Step)",  # 引导模型逐步推导
            "约束条件 (Constraint)",  # 添加各种限制条件
            "详细人设 (Persona)",  # 构建完整的人物设定
        ],
    )

    user_input = st.text_area("输入你的问题/内容", "解释什么是机器学习",
                              height=100)  # 多行文本输入框，接收用户的原始问题

    if technique == "直接提问 (Basic)":  # 如果选择了"直接提问"
        prompt = basic_prompt(user_input)  # 调用基础 Prompt 函数，直接返回用户输入
        code_showcase(  # 展示对应的 Python 调用代码
            "代码", "from prompts.basics import basic_prompt\n\nprompt = basic_prompt(user_input)")  # 显示调用示例代码

    elif technique == "角色设定 (Role)":  # 如果选择了"角色设定"
        role = st.text_input("角色", "机器学习专家")  # 单行文本输入，让用户填写角色名称
        prompt = role_prompt(user_input, role)  # 调用角色设定函数，将角色和用户输入组合成 Prompt
        # 展示调用代码，含当前角色值
        code_showcase("代码", f'prompt = role_prompt(user_input, "{role}")')

    elif technique == "指令明确 (Instruction)":  # 如果选择了"指令明确"
        instruction = st.text_input("指令", "用三句话概括")  # 单行文本输入，让用户填写具体指令
        prompt = instruction_prompt(
            user_input, instruction)  # 调用指令函数，将指令和用户输入组合
        code_showcase(
            "代码", f'prompt = instruction_prompt(user_input, "{instruction}")')  # 展示调用代码

    elif technique == "提供上下文 (Context)":  # 如果选择了"提供上下文"
        context = st.text_area(
            "上下文", "我正在准备一场关于 AI 的演讲，听众是非技术人员")  # 多行文本输入，填写背景信息
        prompt = context_prompt(user_input, context)  # 调用上下文函数，将背景和用户问题组合
        code_showcase(
            "代码", "prompt = context_prompt(user_input, context)")  # 展示调用代码

    elif technique == "格式约束 (Format)":  # 如果选择了"格式约束"
        fmt = st.text_input("格式要求", "Markdown 格式，使用列表和加粗")  # 单行文本输入，填写输出格式要求
        prompt = format_prompt(user_input, fmt)  # 调用格式约束函数，将格式要求附加到用户输入
        code_showcase(
            "代码", f'prompt = format_prompt(user_input, "{fmt}")')  # 展示调用代码

    elif technique == "分步思考 (Step-by-Step)":  # 如果选择了"分步思考"
        prompt = step_by_step_prompt(user_input)  # 调用分步思考函数，引导模型按步骤回答
        code_showcase(
            "代码", "prompt = step_by_step_prompt(user_input)")  # 展示调用代码

    elif technique == "约束条件 (Constraint)":  # 如果选择了"约束条件"
        constraints_input = st.text_area(  # 多行文本输入，每行一个约束条件
            "约束条件（每行一个）", "回答不超过100字\n使用中文\n避免专业术语")  # 标签和默认值
        constraints = [c.strip()  # 将输入文本按行分割，去掉首尾空白
                       for c in constraints_input.split("\n") if c.strip()]  # 过滤掉空行
        prompt = constraint_prompt(
            user_input, constraints)  # 调用约束函数，将约束列表附加到用户输入
        code_showcase(
            "代码", "prompt = constraint_prompt(user_input, constraints)")  # 展示调用代码

    elif technique == "详细人设 (Persona)":  # 如果选择了"详细人设"
        st.info("使用预设人设模板")  # 显示蓝色信息提示框
        persona = {  # 定义一个预设的人物设定字典
            "name": "李老师",  # 姓名
            "职业": "大学教授",  # 职业
            "教学风格": "喜欢用生活中的类比解释复杂概念",  # 教学特点
            "语气": "亲切、耐心",  # 语气风格
            "回答结构": "先给出直观理解，再展开细节",  # 回答结构要求
        }
        prompt = persona_prompt(user_input, persona)  # 调用人设函数，将人设字典和用户输入组合
        code_showcase(
            "代码", "persona = {\"name\": \"李老师\", \"职业\": \"大学教授\", ...}\nprompt = persona_prompt(user_input, persona)")  # 展示调用代码

    st.divider()  # 显示水平分割线，分隔参数区域和生成结果区域
    st.subheader("生成的 Prompt")  # 显示"生成的 Prompt"小标题
    st.code(prompt, language="text")  # 以代码块形式展示最终生成的 Prompt

    if st.button("🚀 调用 LLM 查看效果") and check_api_key():  # 如果用户点击按钮且已配置 API Key
        with st.spinner("正在生成..."):  # 显示加载动画
            try:  # 异常捕获，防止 API 调用出错导致页面崩溃
                from openai import OpenAI  # 在函数内导入 OpenAI 客户端（延迟导入）
                from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL  # 导入 API 配置
                client = OpenAI(api_key=OPENAI_API_KEY,  # 创建 OpenAI 客户端实例
                                base_url=OPENAI_BASE_URL)  # 使用配置中的 Base URL（当前指向 DeepSeek）
                response = client.chat.completions.create(  # 调用聊天补全 API
                    model=DEFAULT_LLM_MODEL,  # 使用配置的默认模型（如 deepseek-chat）
                    # 将生成的 Prompt 作为用户消息发送
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,  # 温度参数，控制回答的创造性（0.7 为适中）
                )
                st.markdown("**LLM 回答：**")  # 显示粗体标题
                # 显示 LLM 返回的回答内容
                st.markdown(response.choices[0].message.content)
            except Exception as e:  # 捕获所有异常
                st.error(f"调用失败：{e}")  # 以红色错误框显示失败原因

elif technique_category == "进阶技巧":  # 如果用户选择了"进阶技巧"
    st.header("进阶 Prompt 技巧")  # 显示进阶技巧区域标题

    technique = st.selectbox(  # 下拉选择框，让用户选择具体的进阶技巧
        "选择技巧",  # 下拉框标签
        [  # 6 个进阶技巧选项
            "Few-Shot 示例学习",  # 通过示例教模型如何回答
            "Chain-of-Thought 思维链",  # 引导模型展示推理过程
            "Self-Consistency 自一致性",  # 多角度思考选择最一致答案
            "Tree-of-Thoughts 思维树",  # 树状探索多种可能性
            "ReAct 模板",  # 推理与行动交替进行
            "自动 Prompt 工程 (APE)",  # 让模型自己优化 Prompt
        ],
    )

    if technique == "Few-Shot 示例学习":  # 如果选择了"Few-Shot"
        st.markdown("通过提供输入-输出示例，教会模型如何回答。")  # 显示该技巧说明
        user_input = st.text_area("测试输入", "这家餐厅的服务太糟糕了")  # 多行文本输入框

        examples = [  # 预设的 Few-Shot 示例列表
            {"input": "今天天气真好，适合出游", "output": "正面"},  # 示例 1：输入和期望输出
            {"input": "这部电影太烂了，浪费钱", "output": "负面"},  # 示例 2
            {"input": "产品质量一般，无功无过", "output": "中性"},  # 示例 3
        ]
        instruction = "判断以下句子的情感倾向（正面/负面/中性）"  # 任务说明文字
        # 调用 Few-Shot 函数生成 Prompt
        prompt = few_shot_prompt(user_input, examples, instruction)

        with st.expander("查看示例数据"):  # 可折叠展开区域
            st.json(examples)  # 以 JSON 格式展示示例数据

        code_showcase(
            "代码", "examples = [{\"input\": \"...\", \"output\": \"...\"}]\nprompt = few_shot_prompt(user_input, examples, instruction)")  # 展示调用代码

    elif technique == "Chain-of-Thought 思维链":  # 如果选择了"思维链"
        st.markdown("引导模型展示推理过程，而非直接给出答案。")  # 显示技巧说明
        user_input = st.text_area(
            "问题", "一个农场有鸡和兔共35只，脚共94只。鸡和兔各有多少只？")  # 多行文本输入
        prompt = chain_of_thought_prompt(user_input)  # 调用思维链函数，引导逐步推理
        code_showcase(
            "代码", "prompt = chain_of_thought_prompt(user_input)")  # 展示调用代码

    elif technique == "Self-Consistency 自一致性":  # 如果选择了"自一致性"
        st.markdown("让模型从多个角度思考，选择最一致的答案。")  # 显示技巧说明
        user_input = st.text_area("问题", "如何提高代码的可维护性？")  # 多行文本输入
        num_paths = st.slider("思考角度数", 2, 5, 3)  # 滑块组件，选择思考路径数量（2-5，默认3）
        prompt = self_consistency_prompt(
            user_input, num_paths)  # 调用自一致性函数，指定路径数
        code_showcase(
            "代码", f"prompt = self_consistency_prompt(user_input, {num_paths})")  # 展示调用代码，含当前路径数

    elif technique == "Tree-of-Thoughts 思维树":  # 如果选择了"思维树"
        st.markdown("在每个思考步骤探索多种可能性，像树一样分支。")  # 显示技巧说明
        user_input = st.text_area("问题", "设计一个高性能的Web API")  # 多行文本输入
        prompt = tree_of_thoughts_prompt(
            user_input, num_branches=3, depth=2)  # 调用思维树函数，指定分支数3层深2
        code_showcase(
            "代码", "prompt = tree_of_thoughts_prompt(user_input, num_branches=3, depth=2)")  # 展示调用代码

    elif technique == "ReAct 模板":  # 如果选择了"ReAct"
        st.markdown("ReAct = Reasoning + Acting，让模型交替进行思考和行动。")  # 显示技巧说明
        prompt = react_prompt_template()  # 调用 ReAct 模板函数，返回模板字符串
        st.info("这是一个模板函数，需要传入 tools_description 和 question")  # 显示蓝色信息提示
        code_showcase(
            "代码", 'prompt = react_prompt_template()\nformatted = prompt.format(tools_description="...", question="...")')  # 展示调用代码
        # 展示格式化后的样子
        tools_desc = "- search: 搜索网络信息\n- calculator: 计算数学表达式"  # 预设工具描述示例
        question = "2024年诺贝尔奖得主是谁？"  # 预设问题示例
        formatted = prompt.format(  # 使用示例参数格式化模板
            tools_description=tools_desc, question=question)  # 传入工具和问题参数
        prompt = formatted  # 将格式化后的结果赋值给 prompt 用于展示

    elif technique == "自动 Prompt 工程 (APE)":  # 如果选择了"APE"
        st.markdown("让模型自己分析和优化 Prompt。")  # 显示技巧说明
        task = st.text_area("任务描述", "从文本中提取人名、地点和时间")  # 多行文本输入，描述任务
        initial = st.text_area("初始 Prompt（可选）", "")  # 多行文本输入，可选的初始 Prompt
        prompt = automatic_prompt_engineering_prompt(
            task, initial)  # 调用 APE 函数，传入任务和初始 Prompt
        code_showcase(
            "代码", "prompt = automatic_prompt_engineering_prompt(task_description, initial_prompt)")  # 展示调用代码

    st.divider()  # 显示水平分割线
    st.subheader("生成的 Prompt")  # 显示"生成的 Prompt"小标题
    st.code(prompt, language="text")  # 以代码块形式展示最终生成的 Prompt

    if st.button("🚀 调用 LLM 查看效果") and check_api_key():  # 如果用户点击按钮且已配置 API Key
        with st.spinner("正在生成..."):  # 显示加载动画
            try:  # 异常捕获
                from openai import OpenAI  # 在函数内导入 OpenAI 客户端
                from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL  # 导入 API 配置
                client = OpenAI(api_key=OPENAI_API_KEY,  # 创建 OpenAI 客户端实例
                                base_url=OPENAI_BASE_URL)  # 使用配置的 Base URL
                response = client.chat.completions.create(  # 调用聊天补全 API
                    model=DEFAULT_LLM_MODEL,  # 使用默认模型
                    # 发送生成的 Prompt
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,  # 温度参数 0.7
                )
                st.markdown("**LLM 回答：**")  # 显示粗体标题
                st.markdown(response.choices[0].message.content)  # 显示 LLM 回答
            except Exception as e:  # 捕获异常
                st.error(f"调用失败：{e}")  # 显示错误信息

elif technique_category == "🤖 智能优化":  # 如果用户选择了"智能优化"
    st.header("🤖 智能 Prompt 优化")  # 显示智能优化区域标题
    st.markdown("""
    输入你的原始问题，AI 会自动分析并选择最适合的 Prompt 技巧组合，
    生成优化后的完整 Prompt。
    """)  # 说明智能优化的作用

    user_input = st.text_area(
        "输入你的原始问题", "用 Python 写个快速排序，要注释详细", height=100)  # 多行文本输入，接收用户原始问题

    if st.button("🔍 智能优化") and check_api_key():  # 如果用户点击"智能优化"按钮且已配置 API Key
        with st.spinner("正在分析并优化 Prompt..."):  # 显示加载动画
            try:  # 异常捕获
                # 调用智能优化函数，让 LLM 自动分析并生成最佳 Prompt
                optimized = auto_optimize_prompt(user_input)
                st.subheader("优化后的 Prompt")  # 显示"优化后的 Prompt"小标题
                st.code(optimized, language="text")  # 以代码块展示 LLM 优化后的完整 Prompt

                if st.button("🚀 调用 LLM 查看效果"):  # 如果用户点击"调用 LLM"按钮
                    with st.spinner("正在生成..."):  # 显示加载动画
                        from openai import OpenAI  # 在函数内导入 OpenAI 客户端
                        from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM_MODEL  # 导入 API 配置
                        client = OpenAI(api_key=OPENAI_API_KEY,  # 创建 OpenAI 客户端实例
                                        base_url=OPENAI_BASE_URL)  # 使用配置的 Base URL
                        response = client.chat.completions.create(  # 调用聊天补全 API
                            model=DEFAULT_LLM_MODEL,  # 使用默认模型
                            # 发送优化后的 Prompt
                            messages=[{"role": "user", "content": optimized}],
                            temperature=0.7,  # 温度参数 0.7
                        )
                        st.markdown("**LLM 回答：**")  # 显示粗体标题
                        # 显示 LLM 回答
                        st.markdown(response.choices[0].message.content)
            except Exception as e:  # 捕获异常
                st.error(f"优化失败：{e}")  # 显示错误信息
