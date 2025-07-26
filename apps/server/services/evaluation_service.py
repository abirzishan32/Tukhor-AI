from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import statistics
from utils.database import DatabaseManager
from services.embedding_service import EmbeddingService
from utils.logger import logger


class EvaluationService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def calculate_groundedness(
        self, answer: str, sources: List[Dict[str, Any]]
    ) -> float:
        """Check if answer is grounded in sources"""
        try:
            if not sources or not answer:
                return 0.0

            answer_embedding = self.embedding_service.encode_text(answer)
            source_texts = [source["content"] for source in sources]
            source_embeddings = self.embedding_service.encode_batch(source_texts)

            similarities = cosine_similarity([answer_embedding], source_embeddings)[0]

            # Return the maximum similarity as groundedness score
            return float(np.max(similarities))

        except Exception as e:
            logger.error(f"Error calculating groundedness: {str(e)}")
            return 0.0

    def calculate_relevance(
        self, query: str, retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """Check relevance of retrieved chunks to query"""
        try:
            if not retrieved_chunks or not query:
                return 0.0

            query_embedding = self.embedding_service.encode_text(query)
            chunk_texts = [chunk["content"] for chunk in retrieved_chunks]
            chunk_embeddings = self.embedding_service.encode_batch(chunk_texts)

            similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]

            # Return the average similarity as relevance score
            return float(np.mean(similarities))

        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return 0.0

    def calculate_answer_quality_metrics(
        self, query: str, answer: str, sources: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate comprehensive answer quality metrics"""
        try:
            # Basic metrics
            groundedness = self.calculate_groundedness(answer, sources)
            relevance = self.calculate_relevance(query, sources)

            # Answer completeness (based on length and structure)
            completeness = self._calculate_completeness(answer)

            # Language consistency (answer should match query language)
            language_consistency = self._check_language_consistency(query, answer)

            # Source utilization (how well sources are used)
            source_utilization = self._calculate_source_utilization(answer, sources)

            return {
                "groundedness": groundedness,
                "relevance": relevance,
                "completeness": completeness,
                "language_consistency": language_consistency,
                "source_utilization": source_utilization,
                "overall_score": (
                    groundedness
                    + relevance
                    + completeness
                    + language_consistency
                    + source_utilization
                )
                / 5,
            }

        except Exception as e:
            logger.error(f"Error calculating answer quality metrics: {str(e)}")
            return {
                "groundedness": 0.0,
                "relevance": 0.0,
                "completeness": 0.0,
                "language_consistency": 0.0,
                "source_utilization": 0.0,
                "overall_score": 0.0,
            }

    def _calculate_completeness(self, answer: str) -> float:
        """Calculate answer completeness based on length and structure"""
        if not answer:
            return 0.0

        # Basic length score
        word_count = len(answer.split())
        length_score = min(word_count / 20, 1.0)  # Optimal around 20 words

        # Structure score (has proper sentences)
        sentences = answer.split("।") + answer.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]
        structure_score = min(len(sentences) / 3, 1.0)  # 2-3 sentences is good

        return (length_score + structure_score) / 2

    def _check_language_consistency(self, query: str, answer: str) -> float:
        """Check if answer language matches query language"""

        # Count Bengali and English characters in query
        query_bengali = len(re.findall(r"[\u0980-\u09FF]", query))
        query_english = len(re.findall(r"[a-zA-Z]", query))

        # Count Bengali and English characters in answer
        answer_bengali = len(re.findall(r"[\u0980-\u09FF]", answer))
        answer_english = len(re.findall(r"[a-zA-Z]", answer))

        # Determine dominant language in query
        query_total = query_bengali + query_english
        answer_total = answer_bengali + answer_english

        if query_total == 0 or answer_total == 0:
            return 0.5

        query_bengali_ratio = query_bengali / query_total
        answer_bengali_ratio = answer_bengali / answer_total

        # Calculate consistency score
        difference = abs(query_bengali_ratio - answer_bengali_ratio)
        consistency = 1.0 - difference

        return max(consistency, 0.0)

    def _calculate_source_utilization(
        self, answer: str, sources: List[Dict[str, Any]]
    ) -> float:
        """Calculate how well the answer utilizes the provided sources"""
        if not sources:
            return 0.0

        # Check if answer seems to be based on sources
        answer_words = set(answer.lower().split())

        utilization_scores = []
        for source in sources:
            source_words = set(source["content"].lower().split())
            overlap = len(answer_words.intersection(source_words))
            overlap_ratio = overlap / max(len(answer_words), 1)
            utilization_scores.append(overlap_ratio)

        # Return average utilization
        return statistics.mean(utilization_scores) if utilization_scores else 0.0

    async def evaluate_response(
        self,
        query: str,
        answer: str,
        sources: List[Dict[str, Any]],
        message_id: Optional[str] = None,
    ) -> Dict[str, float]:
        """Complete evaluation of a RAG response"""
        try:
            metrics = self.calculate_answer_quality_metrics(query, answer, sources)

            # Store evaluation in database if message_id provided
            if message_id:
                await self._store_evaluation(message_id, metrics)

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            raise

    async def _store_evaluation(self, message_id: str, metrics: Dict[str, float]):
        """Store evaluation metrics in database"""
        try:

            async def operation(db):
                await db.queryevaluation.create(
                    data={
                        "messageId": message_id,
                        "groundedness": metrics["groundedness"],
                        "relevance": metrics["relevance"],
                    }
                )

            await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error storing evaluation for message {message_id}: {str(e)}")
            # Don't raise error as this is supplementary data

    async def store_user_feedback(self, message_id: str, feedback: str):
        """Store user feedback for a response"""
        try:

            async def operation(db):
                # Update existing evaluation or create new one
                existing = await db.queryevaluation.find_unique(
                    where={"messageId": message_id}
                )

                if existing:
                    await db.queryevaluation.update(
                        where={"messageId": message_id}, data={"userFeedback": feedback}
                    )
                else:
                    await db.queryevaluation.create(
                        data={"messageId": message_id, "userFeedback": feedback}
                    )

                logger.info(
                    f"Stored user feedback '{feedback}' for message {message_id}"
                )

            await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error storing user feedback: {str(e)}")
            raise

    async def get_evaluation_stats(self) -> Dict[str, Any]:
        """Get overall evaluation statistics"""
        try:

            async def operation(db):
                evaluations = await db.queryevaluation.find_many()

                if not evaluations:
                    return {
                        "total_evaluations": 0,
                        "avg_groundedness": 0.0,
                        "avg_relevance": 0.0,
                        "feedback_distribution": {},
                    }

                # Calculate averages
                groundedness_scores = [
                    e.groundedness for e in evaluations if e.groundedness is not None
                ]
                relevance_scores = [
                    e.relevance for e in evaluations if e.relevance is not None
                ]

                # Feedback distribution
                feedback_counts = {}
                for e in evaluations:
                    if e.userFeedback:
                        feedback_counts[e.userFeedback] = (
                            feedback_counts.get(e.userFeedback, 0) + 1
                        )

                return {
                    "total_evaluations": len(evaluations),
                    "avg_groundedness": (
                        statistics.mean(groundedness_scores)
                        if groundedness_scores
                        else 0.0
                    ),
                    "avg_relevance": (
                        statistics.mean(relevance_scores) if relevance_scores else 0.0
                    ),
                    "feedback_distribution": feedback_counts,
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting evaluation stats: {str(e)}")
            raise
