from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config.settings import settings
from utils.logger import logger
import asyncio


class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self._load_model()

    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.dimension = self._model.get_sentence_embedding_dimension()
            logger.info(
                f"Embedding model loaded successfully. Dimension: {self.dimension}"
            )
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise

    def encode_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if not text or not text.strip():
                return [0.0] * self.dimension

            embedding = self._model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text: {str(e)}")
            raise

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if not texts:
                return []

            # Filter out empty texts
            valid_texts = [text for text in texts if text and text.strip()]

            if not valid_texts:
                return [[0.0] * self.dimension] * len(texts)

            embeddings = self._model.encode(valid_texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error encoding batch texts: {str(e)}")
            raise

    async def encode_text_async(self, text: str) -> List[float]:
        """Async wrapper for text encoding"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.encode_text, text
        )

    async def encode_batch_async(self, texts: List[str]) -> List[List[float]]:
        """Async wrapper for batch encoding"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.encode_batch, texts
        )

    def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
