"""PDF Processor Component - Handles PDF upload, validation, and text extraction."""

import io
from typing import Dict
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


class InvalidPDFError(Exception):
    """Raised when PDF file is invalid or corrupted."""
    pass


class FileReadError(Exception):
    """Raised when file cannot be read."""
    pass


class PDFProcessor:
    """Handles PDF validation and text extraction."""

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    def __init__(self):
        """Initialize PDF Processor."""
        self.preferred_lib = 'pdfplumber' if pdfplumber else 'PyPDF2'

    def validate(self, pdf_file) -> bool:
        """
        Validate PDF file format and integrity.

        Args:
            pdf_file: File-like object (from request.files in Flask)

        Returns:
            True if valid

        Raises:
            InvalidPDFError: If PDF is invalid
            FileReadError: If file cannot be read
        """
        if not pdf_file or pdf_file.filename == '':
            raise InvalidPDFError("No file selected")

        # Check file size
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset to start

        if file_size > self.MAX_FILE_SIZE:
            raise InvalidPDFError(f"File too large (max {self.MAX_FILE_SIZE / 1024 / 1024}MB)")

        if file_size == 0:
            raise InvalidPDFError("File is empty")

        # Check PDF magic bytes
        pdf_file.seek(0)
        header = pdf_file.read(4)
        pdf_file.seek(0)

        if header != b'%PDF':
            raise InvalidPDFError("Not a valid PDF file")

        # Try to parse as PDF
        try:
            if pdfplumber:
                pdfplumber.open(io.BytesIO(pdf_file.read()))
            elif PdfReader:
                PdfReader(io.BytesIO(pdf_file.read()))
            else:
                raise InvalidPDFError("No PDF library available")
            pdf_file.seek(0)
            return True
        except Exception as e:
            raise InvalidPDFError(f"PDF parsing failed: {str(e)}")

    def extract_text(self, pdf_file) -> str:
        """
        Extract readable text from PDF.

        Args:
            pdf_file: File-like object

        Returns:
            Extracted text string

        Raises:
            FileReadError: If text extraction fails
        """
        try:
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()

            # Try pdfplumber first (better text extraction)
            if pdfplumber:
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    text_parts = []
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            text_parts.append(f"--- Page {page_num} ---\n{text}")
                    return "\n\n".join(text_parts)

            # Fallback to PyPDF2
            elif PdfReader:
                pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                return "\n\n".join(text_parts)

            else:
                raise FileReadError("No PDF library available for text extraction")

        except Exception as e:
            raise FileReadError(f"Failed to extract text: {str(e)}")

    def get_metadata(self, pdf_file) -> Dict[str, any]:
        """
        Extract PDF metadata (filename, page count, etc.).

        Args:
            pdf_file: File-like object

        Returns:
            Dictionary with metadata
        """
        try:
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)

            filename = getattr(pdf_file, 'filename', 'document.pdf')

            # Get page count
            page_count = 0
            if pdfplumber:
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    page_count = len(pdf.pages)
            elif PdfReader:
                pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                page_count = len(pdf_reader.pages)

            return {
                'filename': filename,
                'page_count': page_count,
                'file_size': len(pdf_bytes),
                'upload_timestamp': None  # Set by API layer
            }
        except Exception as e:
            return {
                'filename': getattr(pdf_file, 'filename', 'document.pdf'),
                'page_count': 0,
                'file_size': 0,
                'error': str(e)
            }
