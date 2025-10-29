import logging
from typing import Optional
from pdfminer.high_level import extract_text as pdf_extract_text
import docx2txt
import tempfile
import os

logger = logging.getLogger(__name__)


class FileExtractor:
    """
    Extract text from PDF and DOCX files
    Uses pdfminer.six and docx2txt for accurate extraction
    """

    @staticmethod
    def extract_text_from_file(file_content: bytes, filename: str) -> str:
        """
        Extract text from uploaded file
        Supports: PDF, DOCX
        Returns: Clean text content
        """
        try:
            file_extension = filename.lower().split('.')[-1]
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            try:
                if file_extension == 'pdf':
                    text = FileExtractor.extract_text_from_pdf(temp_path)
                elif file_extension in ['doc', 'docx']:
                    text = FileExtractor.extract_text_from_docx(temp_path)
                else:
                    logger.warning(f"Unsupported file type: {file_extension}")
                    text = ""
                
                return text
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"File extraction error: {e}")
            return ""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF using pdfminer.six"""
        try:
            text = pdf_extract_text(file_path)
            logger.info(f"✅ Extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX using docx2txt"""
        try:
            text = docx2txt.process(file_path)
            logger.info(f"✅ Extracted {len(text)} characters from DOCX")
            return text
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""

    @staticmethod
    def clean_text(text: str, max_length: int = 15000) -> str:
        """
        Clean and truncate text for Gemini API
        Removes excessive whitespace and limits length
        """
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Remove URLs
        import re
        cleaned = re.sub(r'http\S+|www\.\S+', '', cleaned)
        
        # Truncate if too long (Gemini has limits)
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
            logger.info(f"Truncated text to {max_length} characters")
        
        return cleaned


# Global instance
file_extractor = FileExtractor()

