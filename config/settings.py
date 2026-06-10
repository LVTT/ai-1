"""项目全局配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# LLM 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# RAG 配置
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma_db"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "4"))

# Agent 配置
MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "5"))
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "60"))

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
KD_CRM_DOCS_DIR = DATA_DIR / "kd_crm_docs"


def check_api_key() -> bool:
    """检查 API Key 是否已配置"""
    return bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here")
