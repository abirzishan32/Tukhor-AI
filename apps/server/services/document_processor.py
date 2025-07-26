import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config.settings import settings
from utils.logger import logger
import requests


class DocumentProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        # Custom splitter for Bengali text
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "।", ".", "!", "?", ";", ":", " ", ""],
        )

    async def download_pdf_from_url(self, url: str) -> bytes:
        """Download PDF from URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading PDF from URL {url}: {str(e)}")
            raise

    def extract_text_from_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract text and metadata from PDF"""
        try:
            # Use PyMuPDF for extraction
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

            text_content = ""
            page_texts = []

            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                page_texts.append({"page": page_num + 1, "text": page_text})
                text_content += page_text + "\n\n"

            # Extract metadata
            metadata = {
                "page_count": pdf_document.page_count,
                "pages": page_texts,
                "title": pdf_document.metadata.get("title", ""),
                "author": pdf_document.metadata.get("author", ""),
                "subject": pdf_document.metadata.get("subject", ""),
                "creator": pdf_document.metadata.get("creator", ""),
            }

            pdf_document.close()

            return {
                "content": text_content,
                "metadata": metadata,
                "word_count": len(text_content.split()),
                "page_count": metadata["page_count"],
            }

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def clean_bengali_text(self, text: str) -> str:
        """Clean and normalize Bengali text"""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep Bengali punctuation
        text = re.sub(
            r'[^\u0980-\u09FF\u0964-\u0965a-zA-Z0-9\s।,;:.!?()"\'-]', "", text
        )

        # Normalize whitespace around Bengali punctuation
        text = re.sub(r"\s*।\s*", "। ", text)
        text = re.sub(r"\s*,\s*", ", ", text)

        # Remove multiple newlines
        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    def detect_language(self, text: str) -> str:
        """Detect if text is Bengali, English, or mixed"""
        bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        total_chars = bengali_chars + english_chars

        if total_chars == 0:
            return "en"

        bengali_ratio = bengali_chars / total_chars

        if bengali_ratio > 0.7:
            return "bn"
        elif bengali_ratio < 0.3:
            return "en"
        else:
            return "mixed"

    def chunk_document(
        self, text: str, metadata: Dict, document_title: str = ""
    ) -> List[Document]:
        """Split document into chunks with proper metadata"""
        try:
            # Clean the text
            cleaned_text = self.clean_bengali_text(text)

            # Detect language
            language = self.detect_language(cleaned_text)

            # Split into chunks
            chunks = self.text_splitter.split_text(cleaned_text)

            documents = []
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # Skip very short chunks
                    continue

                chunk_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "language": language,
                    "document_title": document_title,
                    "chunk_length": len(chunk),
                    "word_count": len(chunk.split()),
                }

                documents.append(Document(page_content=chunk, metadata=chunk_metadata))

            return documents

        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            raise

    async def process_knowledge_base(self) -> List[Document]:
        """Process the knowledge base document"""
        try:
            logger.info("Processing knowledge base document...")

            # Download the knowledge base PDF
            pdf_content = await self.download_pdf_from_url(settings.KNOWLEDGE_BASE_URL)

            # Extract text and metadata
            extracted_data = self.extract_text_from_pdf(pdf_content)

            # Create chunks
            chunks = self.chunk_document(
                text=extracted_data["content"],
                metadata=extracted_data["metadata"],
                document_title="HSC26 Bangla 1st Paper",
            )

            logger.info(
                f"Successfully processed knowledge base: {len(chunks)} chunks created"
            )
            return chunks

        except Exception as e:
            logger.error(f"Error processing knowledge base: {str(e)}")
            raise

    async def process_uploaded_document(
        self, file_content: bytes, filename: str, file_type: str
    ) -> List[Document]:
        """Process an uploaded document"""
        try:
            if file_type.lower() == "pdf":
                extracted_data = self.extract_text_from_pdf(file_content)

                chunks = self.chunk_document(
                    text=extracted_data["content"],
                    metadata=extracted_data["metadata"],
                    document_title=filename,
                )

                return chunks
            else:
                # Handle other file types (text, etc.)
                text_content = file_content.decode("utf-8")

                chunks = self.chunk_document(
                    text=text_content,
                    metadata={"filename": filename, "file_type": file_type},
                    document_title=filename,
                )

                return chunks

        except Exception as e:
            logger.error(f"Error processing uploaded document {filename}: {str(e)}")
            raise
