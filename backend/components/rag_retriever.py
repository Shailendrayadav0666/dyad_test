"""RAG Retriever Component - Query embedding and context retrieval from vector store."""

from typing import List, Dict, Any, Optional
from backend.components.embedding_engine import EmbeddingEngine, EmbeddingError
from backend.components.vector_store import VectorStore, VectorStoreError


class RAGRetrieverError(Exception):
    """Raised when RAG retrieval operations fail."""
    pass


class RAGRetriever:
    """Retrieves semantically similar document chunks for RAG context."""

    DEFAULT_TOP_K = 5

    def __init__(self, embedding_engine: EmbeddingEngine):
        """
        Initialize RAG Retriever.

        Args:
            embedding_engine: EmbeddingEngine instance for query embedding
        """
        if not embedding_engine:
            raise RAGRetrieverError("EmbeddingEngine instance required")

        self.embedding_engine = embedding_engine

    def retrieve_context(
        self,
        query: str,
        vector_store: VectorStore,
        collection_name: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve semantically similar chunks from vector store.

        Args:
            query: User query string
            vector_store: VectorStore instance with indexed embeddings
            collection_name: Qdrant collection to search
            top_k: Number of results to return (default: 5)
            score_threshold: Minimum similarity score (optional)

        Returns:
            List of context chunks sorted by relevance (highest first)

        Raises:
            RAGRetrieverError: If retrieval fails
        """
        if not query or len(query.strip()) == 0:
            raise RAGRetrieverError("Query cannot be empty")

        if not vector_store or not collection_name:
            raise RAGRetrieverError("Vector store and collection name required")

        top_k = top_k or self.DEFAULT_TOP_K

        try:
            # Step 1: Convert query to embedding vector
            query_embedding = self._embed_query(query)

            # Step 2: Search vector store for similar chunks
            search_results = vector_store.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold
            )

            # Step 3: Format results
            context_chunks = self._format_results(search_results)

            return context_chunks

        except EmbeddingError as e:
            raise RAGRetrieverError(f"Query embedding failed: {str(e)}")
        except VectorStoreError as e:
            raise RAGRetrieverError(f"Vector store search failed: {str(e)}")
        except Exception as e:
            raise RAGRetrieverError(f"Retrieval failed: {str(e)}")

    def _embed_query(self, query: str) -> List[float]:
        """
        Convert query string to embedding vector.

        Args:
            query: Query text

        Returns:
            Query embedding vector (384-dimensional)

        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            # Generate embedding for single query
            embeddings = self.embedding_engine.model.encode(
                [query],
                convert_to_numpy=True
            )

            # Return first (only) embedding as list
            return embeddings[0].tolist()

        except Exception as e:
            raise EmbeddingError(f"Failed to embed query: {str(e)}")

    def _format_results(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format search results for LLM consumption.

        Args:
            search_results: Raw Qdrant search results

        Returns:
            Formatted context chunks with ranking and metadata
        """
        formatted = []

        for rank, result in enumerate(search_results, 1):
            chunk = {
                'rank': rank,
                'chunk_text': result.get('chunk_text', ''),
                'similarity_score': round(result.get('similarity_score', 0.0), 4),
                'chunk_size': result.get('chunk_size', 0),
                'point_id': result.get('point_id', '')
            }
            formatted.append(chunk)

        return formatted

    def get_context_string(
        self,
        context_chunks: List[Dict[str, Any]],
        separator: str = "\n---\n"
    ) -> str:
        """
        Convert context chunks to a formatted string for LLM prompt.

        Args:
            context_chunks: List of context chunks from retrieve_context()
            separator: Separator between chunks (default: newline + separator)

        Returns:
            Formatted context string with rankings and scores
        """
        if not context_chunks:
            return ""

        context_lines = []

        for chunk in context_chunks:
            score = chunk.get('similarity_score', 0.0)
            text = chunk.get('chunk_text', '')
            rank = chunk.get('rank', 0)

            # Format: [#1, score=0.8234] chunk text...
            header = f"[#{rank}, score={score}]"
            context_lines.append(f"{header}\n{text}")

        return separator.join(context_lines)

