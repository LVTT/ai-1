"""文档加载模块

支持多种文档格式的加载与文本提取。
"""

import os
from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass


@dataclass
class Document:
    """统一文档数据结构"""
    content: str
    metadata: dict
    source: str


class DocumentLoader:
    """文档加载器

    支持格式：txt, md, pdf, docx
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self, source: Union[str, Path]) -> List[Document]:
        """加载单个文件或目录"""
        source = Path(source)

        if source.is_dir():
            return self.load_directory(source)
        else:
            doc = self.load_file(source)
            return [doc] if doc else []

    def load_file(self, file_path: Union[str, Path]) -> Optional[Document]:
        """加载单个文件"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".txt" or suffix == ".md":
                return self._load_text(file_path)
            elif suffix == ".pdf":
                return self._load_pdf(file_path)
            elif suffix == ".docx":
                return self._load_docx(file_path)
            else:
                print(f"不支持的文件格式: {suffix}")
                return None
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return None

    def load_directory(self, dir_path: Union[str, Path]) -> List[Document]:
        """加载目录下所有支持的文件"""
        dir_path = Path(dir_path)
        documents = []

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".pdf", ".docx"]:
                doc = self.load_file(file_path)
                if doc:
                    documents.append(doc)

        return documents

    def _load_text(self, file_path: Path) -> Document:
        """加载文本文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return Document(
            content=content,
            metadata={
                "file_name": file_path.name,
                "file_type": "text",
                "file_path": str(file_path),
            },
            source=str(file_path),
        )

    def _load_pdf(self, file_path: Path) -> Document:
        """加载 PDF 文件"""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("请安装 pypdf: pip install pypdf")

        reader = PdfReader(str(file_path))
        texts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)

        content = "\n".join(texts)
        return Document(
            content=content,
            metadata={
                "file_name": file_path.name,
                "file_type": "pdf",
                "file_path": str(file_path),
                "page_count": len(reader.pages),
            },
            source=str(file_path),
        )

    def _load_docx(self, file_path: Path) -> Document:
        """加载 Word 文档"""
        try:
            from docx import Document as DocxDocument
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        doc = DocxDocument(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = "\n".join(paragraphs)

        return Document(
            content=content,
            metadata={
                "file_name": file_path.name,
                "file_type": "docx",
                "file_path": str(file_path),
            },
            source=str(file_path),
        )

    def split_text(self, text: str) -> List[str]:
        """简单文本分块（按字符数）

        生产环境建议使用更智能的分块策略，如：
        - LangChain 的 RecursiveCharacterTextSplitter
        - 按语义分块
        - 按句子/段落分块
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def load_and_split(self, source: Union[str, Path]) -> List[Document]:
        """加载文档并分块"""
        documents = self.load(source)
        split_docs = []

        for doc in documents:
            chunks = self.split_text(doc.content)
            total_len = len(doc.content)
            for i, chunk in enumerate(chunks):
                metadata = doc.metadata.copy()
                metadata["chunk_index"] = i
                metadata["total_chunks"] = len(chunks)
                # 计算这块在原文中的大致位置百分比
                chunk_start = i * (self.chunk_size - self.chunk_overlap)
                metadata["position_percent"] = round(
                    min(100, (chunk_start / max(total_len, 1)) * 100), 1
                )
                split_docs.append(Document(
                    content=chunk,
                    metadata=metadata,
                    source=doc.source,
                ))

        return split_docs
