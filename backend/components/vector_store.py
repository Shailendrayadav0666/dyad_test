"""Vector Store Component - Qdrant in-memory vector database integration."""

from typing import List, Dict, Tuple, Optional, Any
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""
    pass


class VectorStore:
    """Manages vector storage and semantic search using Qdrant in-memory database."""

    DISTANCE_METRIC = Distance.COSINE
    EMBEDDING_DIMENSION = 384  # Must match EmbeddingEngine output

    def __init__(self):
        """
        Initialize Vector Store with in-memory Qdrant instance.

        Raises:
            VectorStoreError: If Qdrant client cannot be initialized
        """
        if not QdrantClient:
            raise VectorStoreError("qdrant-client not installed")

        try:
            # Create in-memory Qdrant instance (no persistent storage)
            self.client = QdrantClient(":memory:")
            self.collections: Dict[str, Dict[str, Any]] = {}
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize Qdrant: {str(e)}")

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = EMBEDDING_DIMENSION
    ) -> str:
        """
        Create a new vector collection.

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors (default: 384)

        Returns:
            collection_name (for chaining)

        Raises:
            VectorStoreError: If collection creation fails
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_names = [c.name for c in collections.collections]

            if collection_name not in existing_names:
                # Create new collection
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=self.DISTANCE_METRIC
                    )
                )

            # Track collection metadata
            self.collections[collection_name] = {
                'name': collection_name,
                'vector_size': vector_size,
                'point_count': 0,
                'created_at': None
            }

            return collection_name

        except Exception as e:
            raise VectorStoreError(f"Failed to create collection '{collection_name}': {str(e)}")

    def store_embeddings(
        self,
        collection_name: str,
        embeddings_data: List[Tuple[str, List[float]]]
    ) -> int:
        """
        Store embeddings in Qdrant collection.

        Args:
            collection_name: Target collection
            embeddings_data: List of (chunk_text, embedding_vector) tuples

        Returns:
            Number of points stored

        Raises:
            VectorStoreError: If storage fails
        """
        if not embeddings_data:
            return 0

        try:
            # Prepare points for insertion
            points = []
            for chunk_text, embedding_vector in embeddings_data:
                # Generate unique ID for each chunk
                point_id = str(uuid.uuid4())

                # Create point with metadata
                point = PointStruct(
                    id=point_id,
                    vector=embedding_vector,
                    payload={
                        'chunk_text': chunk_text,
                        'chunk_size': len(chunk_text),
                        'embedding_model': 'all-MiniLM-L6-v2'
                    }
                )
                points.append(point)

            # Upsert points (insert or update)
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

            # Update collection metadata
            if collection_name in self.collections:
                self.collections[collection_name]['point_count'] += len(points)

            return len(points)

        except Exception as e:
            raise VectorStoreError(f"Failed to store embeddings: {str(e)}")

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in vector collection.

        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector (384-dimensional)
            top_k: Number of results to return (default: 5)
            score_threshold: Minimum similarity score (optional)

        Returns:
            List of search results with chunk text and similarity scores

        Raises:
            VectorStoreError: If search fails
        """
        if not query_vector:
            return []

        if len(query_vector) != self.EMBEDDING_DIMENSION:
            raise VectorStoreError(
                f"Query vector dimension {len(query_vector)} "
                f"does not match expected {self.EMBEDDING_DIMENSION}"
            )

        try:
            # query_points() is the current API (qdrant-client >= 1.7.0);
            # client.search() was removed in 1.12.0
            if hasattr(self.client, 'query_points'):
                response = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold
                )
                search_results = response.points
            else:
                search_results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold
                )

            # Format results
            results = []
            for scored_point in search_results:
                result = {
                    'point_id': scored_point.id,
                    'similarity_score': scored_point.score,
                    'chunk_text': scored_point.payload.get('chunk_text', ''),
                    'chunk_size': scored_point.payload.get('chunk_size', 0)
                }
                results.append(result)

            return results

        except Exception as e:
            raise VectorStoreError(f"Search failed: {str(e)}")

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get collection statistics and metadata.

        Args:
            collection_name: Collection name

        Returns:
            Collection information dictionary

        Raises:
            VectorStoreError: If collection doesn't exist
        """
        try:
            collection_info = self.client.get_collection(collection_name)

            # qdrant-client >= 1.7: size/distance moved to params.vectors (VectorParams)
            vectors_cfg = collection_info.config.params.vectors
            if hasattr(vectors_cfg, 'size'):
                vector_size = vectors_cfg.size
                distance = str(vectors_cfg.distance)
            elif isinstance(vectors_cfg, dict):
                first = next(iter(vectors_cfg.values()))
                vector_size = first.size
                distance = str(first.distance)
            else:
                vector_size = self.EMBEDDING_DIMENSION
                distance = 'Cosine'

            return {
                'name': collection_name,
                'points_count': collection_info.points_count,
                'vector_size': vector_size,
                'distance_metric': distance,
                'status': collection_info.status,
            }

        except Exception as e:
            raise VectorStoreError(f"Failed to get collection info: {str(e)}")

