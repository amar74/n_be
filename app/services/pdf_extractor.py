import logging
from typing import Optional
import PyPDF2
import io
from docx import Document

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extract text from PDF and DOCX files
    Prepares content for Gemini AI analysis
    """

    @staticmethod
    def extract_text_from_file(file_content: bytes, filename: str) -> str:
        """
        Extract text from uploaded CV file
        Supports: PDF, DOCX
        Returns: Plain text content
        """
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return PDFExtractor._extract_from_pdf(file_content)
            elif file_extension in ['doc', 'docx']:
                return PDFExtractor._extract_from_docx(file_content)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return ""

        except Exception as e:
            logger.error(f"File extraction error: {e}")
            return ""

    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            full_text = '\n'.join(text_content)
            logger.info(f"✅ Extracted {len(full_text)} characters from PDF")
            
            return full_text

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            full_text = '\n'.join(text_content)
            logger.info(f"✅ Extracted {len(full_text)} characters from DOCX")
            
            return full_text

        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""

    @staticmethod
    def clean_text(text: str, max_length: int = 15000) -> str:
        """
        Clean and truncate text for Gemini API
        Gemini has context limits, so we keep it focused
        """
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Truncate if too long
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            logger.info(f"Truncated text to {max_length} characters")
        
        return cleaned


# Global instance
pdf_extractor = PDFExtractor()

