"""Content Extraction Module
Extracts text content from PDF and text files"""

import PyPDF2
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extracts content from various file types"""
    
    @staticmethod
    def extract_from_pdf(file_path):
        """Extract text from PDF file"""
        try:
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())
            
            full_text = '\n'.join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from {Path(file_path).name}")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_text(file_path):
        """Extract text from text file"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            logger.info(f"Extracted {len(content)} characters from {Path(file_path).name}")
            return content
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_content(file_path):
        """Main extraction method - routes to appropriate extractor"""
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return ""
        
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return ContentExtractor.extract_from_pdf(file_path)
        elif suffix == '.txt':
            return ContentExtractor.extract_from_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return ""
    
    @staticmethod
    def get_preview(content, max_length=500):
        """Get a preview of the content"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
