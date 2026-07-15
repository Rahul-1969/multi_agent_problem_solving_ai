import os
from utils.logger import get_logger

logger = get_logger(__name__)

class DocumentExtractor:
    @staticmethod
    def extract_text(file_path: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return PDFExtractor.extract(file_path)
        elif ext == ".docx":
            return DOCXExtractor.extract(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

class PDFExtractor:
    @staticmethod
    def extract(file_path: str) -> str:
        try:
            # We'll use the existing PDFReader that exists for other parts
            from tools.pdf_reader import PDFReader
            reader = PDFReader(file_path)
            return reader.get_text()
        except Exception as e:
            logger.error(f"Failed to extract PDF: {e}")
            raise

class DOCXExtractor:
    @staticmethod
    def extract(file_path: str) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except ImportError:
            logger.error("python-docx is not installed. Run 'pip install python-docx'")
            raise
        except Exception as e:
            logger.error(f"Failed to extract DOCX: {e}")
            raise
