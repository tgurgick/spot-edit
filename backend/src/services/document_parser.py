"""Document parsing service for extracting text from various formats."""
from pathlib import Path
from typing import Union
import io


def parse_document(file_content: bytes, filename: str) -> str:
    """
    Parse document and extract text.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        Extracted text from the document

    Raises:
        ValueError: If file format is not supported
    """
    file_extension = Path(filename).suffix.lower()

    if file_extension == ".txt":
        return extract_text_from_txt(file_content)
    elif file_extension == ".pdf":
        return extract_text_from_pdf(file_content)
    elif file_extension in [".docx", ".doc"]:
        return extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from a plain text file.

    Args:
        file_content: File content as bytes

    Returns:
        Text content
    """
    try:
        return file_content.decode("utf-8")
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        return file_content.decode("latin-1")


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_content: File content as bytes

    Returns:
        Extracted text
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")

    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text_parts = []
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)


def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_content: File content as bytes

    Returns:
        Extracted text
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required for DOCX parsing. Install with: pip install python-docx")

    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)

    text_parts = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)

    return "\n\n".join(text_parts)
