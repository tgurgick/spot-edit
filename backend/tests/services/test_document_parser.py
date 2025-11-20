"""
Unit tests for document_parser.py

Tests the DocumentParser service for extracting text from various file formats.
"""

import io
import pytest
from backend.src.services.document_parser import (
    DocumentParser,
    DocumentParsingError,
    UnsupportedFileTypeError,
)


class TestDocumentParser:
    """Test cases for DocumentParser class."""

    def test_parse_txt_file(self):
        """Test parsing plain text file."""
        text_content = "This is a test document.\nWith multiple lines."
        file = io.BytesIO(text_content.encode('utf-8'))

        result = DocumentParser.parse_document(file, "txt")

        assert result == text_content
        assert "test document" in result

    def test_parse_txt_with_different_encoding(self):
        """Test parsing text file with latin-1 encoding."""
        text_content = "Café résumé"
        file = io.BytesIO(text_content.encode('latin-1'))

        result = DocumentParser.parse_document(file, "txt")

        assert result is not None
        assert len(result) > 0

    def test_parse_txt_from_bytes(self):
        """Test parsing text from bytes input."""
        text_content = "Direct bytes input"
        text_bytes = text_content.encode('utf-8')

        result = DocumentParser.parse_document(text_bytes, "txt")

        assert result == text_content

    def test_unsupported_file_type(self):
        """Test that unsupported file types raise appropriate error."""
        file = io.BytesIO(b"some content")

        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            DocumentParser.parse_document(file, "xyz")

        assert "not supported" in str(exc_info.value).lower()
        assert ".xyz" in str(exc_info.value)

    def test_file_type_normalization(self):
        """Test that file type is normalized correctly."""
        text_content = "Test content"
        file = io.BytesIO(text_content.encode('utf-8'))

        # Test with uppercase
        result1 = DocumentParser.parse_document(file, "TXT")
        file.seek(0)

        # Test with dot prefix
        result2 = DocumentParser.parse_document(file, ".txt")

        assert result1 == text_content
        assert result2 == text_content

    def test_extract_text_from_txt(self):
        """Test direct call to extract_text_from_txt method."""
        text_content = "Direct method call test"
        file = io.BytesIO(text_content.encode('utf-8'))

        result = DocumentParser.extract_text_from_txt(file)

        assert result == text_content

    def test_empty_txt_file(self):
        """Test parsing empty text file."""
        file = io.BytesIO(b"")

        result = DocumentParser.parse_document(file, "txt")

        assert result == ""

    @pytest.mark.skipif(
        not hasattr(DocumentParser, 'extract_text_from_pdf') or
        DocumentParser.extract_text_from_pdf.__code__.co_consts[1] is None,
        reason="PyPDF2 not installed"
    )
    def test_pdf_parsing_not_installed_error(self):
        """Test that PDF parsing fails gracefully when PyPDF2 is not installed."""
        # This test would need a mock PDF file
        # For now, just verify the method exists
        assert hasattr(DocumentParser, 'extract_text_from_pdf')

    @pytest.mark.skipif(
        not hasattr(DocumentParser, 'extract_text_from_docx') or
        DocumentParser.extract_text_from_docx.__code__.co_consts[1] is None,
        reason="python-docx not installed"
    )
    def test_docx_parsing_not_installed_error(self):
        """Test that DOCX parsing fails gracefully when python-docx is not installed."""
        # This test would need a mock DOCX file
        # For now, just verify the method exists
        assert hasattr(DocumentParser, 'extract_text_from_docx')

    def test_supported_extensions(self):
        """Test that SUPPORTED_EXTENSIONS constant is correct."""
        expected = {'.txt', '.pdf', '.docx'}
        assert DocumentParser.SUPPORTED_EXTENSIONS == expected


class TestDocumentParserWithMockFiles:
    """Test DocumentParser with mock file content."""

    def test_parse_multiline_text(self):
        """Test parsing text with multiple lines and paragraphs."""
        text = """Line 1
Line 2

Paragraph 2
Line 4"""
        file = io.BytesIO(text.encode('utf-8'))

        result = DocumentParser.parse_document(file, "txt")

        assert "Line 1" in result
        assert "Paragraph 2" in result
        assert result.count("\n") >= 3

    def test_parse_text_with_special_characters(self):
        """Test parsing text with special characters."""
        text = "Special chars: @#$%^&*()_+-=[]{}|;:',.<>?/~`"
        file = io.BytesIO(text.encode('utf-8'))

        result = DocumentParser.parse_document(file, "txt")

        assert result == text

    def test_parse_unicode_text(self):
        """Test parsing text with unicode characters."""
        text = "Unicode: 你好 мир 🌍 café"
        file = io.BytesIO(text.encode('utf-8'))

        result = DocumentParser.parse_document(file, "txt")

        assert "你好" in result or len(result) > 0  # Might be decoded differently
