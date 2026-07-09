"""Embedding Engine Component - Text chunking and vector embedding generation."""

from typing import List, Tuple, Optional
import warnings

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""
    pass


class TextProcessingError(Exception):
    """Raised when text processing fails."""
    pass


class EmbeddingEngine:
    """Handles text chunking and vector embedding generation."""

    # Configuration (from functional design)
    DEFAULT_CHUNK_SIZE = 512  # characters
    DEFAULT_OVERLAP = 50  # characters
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # sentence-transformers
    EMBEDDING_DIMENSION = 384  # output vector dimension
    BATCH_SIZE = 32  # embeddings per batch

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Embedding Engine.

        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name or self.EMBEDDING_MODEL
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the sentence-transformers model."""
        if not SentenceTransformer:
            raise EmbeddingError("sentence-transformers not installed")

        try:
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.model.get_embedding_dimension()
        except Exception as e:
            raise EmbeddingError(f"Failed to load embedding model: {str(e)}")

    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into fixed-size overlapping chunks.

        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters (default: 512)
            overlap: Overlap between chunks in characters (default: 50)

        Returns:
            List of text chunks

        Raises:
            TextProcessingError: If chunking fails
        """
        if not text or len(text.strip()) == 0:
            return []

        chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        overlap = overlap or self.DEFAULT_OVERLAP

        if chunk_size <= 0:
            raise TextProcessingError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise TextProcessingError("overlap must be between 0 and chunk_size")

        chunks = []
        step = chunk_size - overlap  # How many new characters per chunk

        try:
            i = 0
            while i < len(text):
                # Extract chunk
                chunk = text[i:i + chunk_size]

                # Only add non-empty chunks
                if chunk.strip():
                    chunks.append(chunk)

                # Move to next position
                i += step

                # Stop if we've reached the end
                if i >= len(text):
                    break

            return chunks

        except Exception as e:
            raise TextProcessingError(f"Chunking failed: {str(e)}")

    def generate_embeddings(
        self,
        chunks: List[str],
        show_progress: bool = False
    ) -> List[Tuple[str, List[float]]]:
        """
        Generate vector embeddings for text chunks.

        Args:
            chunks: List of text chunks
            show_progress: Whether to show progress bar (default: False)

        Returns:
            List of (chunk_text, embedding_vector) tuples

        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not chunks:
            return []

        try:
            # Suppress progress bar if not requested
            if not show_progress:
                warnings.filterwarnings('ignore')

            # Generate embeddings for all chunks
            embeddings = self.model.encode(
                chunks,
                batch_size=self.BATCH_SIZE,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )

            # Return as list of (chunk, vector) tuples
            result = [
                (chunks[i], embeddings[i].tolist())
                for i in range(len(chunks))
            ]

            return result

        except Exception as e:
            raise EmbeddingError(f"Embedding generation failed: {str(e)}")

    def process(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[Tuple[str, List[float]]]:
        """
        End-to-end: chunk text and generate embeddings.

        Args:
            text: Input text
            chunk_size: Chunk size in characters (default: 512)
            overlap: Overlap in characters (default: 50)

        Returns:
            List of (chunk_text, embedding_vector) tuples

        Raises:
            TextProcessingError: If chunking fails
            EmbeddingError: If embedding fails
        """
        # Step 1: Chunk text
        chunks = self.chunk_text(text, chunk_size, overlap)

        if not chunks:
            return []

        # Step 2: Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the output dimension of embeddings."""
        if self.model is None:
            return self.EMBEDDING_DIMENSION
        return self.embedding_dimension

