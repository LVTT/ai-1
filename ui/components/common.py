"""Streamlit 通用组件"""

import streamlit as st
from typing import Optional, Callable


def api_key_warning():
    """API Key 未配置时的警告"""
    from config.settings import check_api_key
    if not check_api_key():
        st.warning("⚠️ API Key 未配置，部分功能可能无法使用。请检查 `.env` 文件。")
        return False
    return True


def code_showcase(title: str, code: str, language: str = "python"):
    """展示代码示例"""
    with st.expander(f"📖 {title}"):
        st.code(code, language=language)


def llm_response_box(label: str, response: str):
    """展示 LLM 回答"""
    with st.container(border=True):
        st.markdown(f"**{label}**")
        st.markdown(response)


def sidebar_info():
    """侧边栏通用信息"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("🧪 **AI 工程化实验室**")
        st.markdown("[GitHub](https://github.com) · [文档](#)")
