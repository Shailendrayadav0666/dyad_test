"""Answer Generator Component - LLM-based answer generation with citations."""

from typing import List, Dict, Any, Optional, Tuple
import re
import os

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class AnswerGeneratorError(Exception):
    """Raised when answer generation fails."""
    pass


class AnswerGenerator:
    """Generates answers using Claude API with RAG context and citations."""

    # Configuration
    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 1024  # Max tokens in answer
    TEMPERATURE = 0.7  # Balanced creativity/determinism

    # RAG Prompt Template
    RAG_PROMPT_TEMPLATE = """You are a helpful tutor answering questions about exam materials.

Based on the following context from the course materials, answer the student's question accurately and concisely.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Answer Generator with Claude API.

        Args:
            api_key: Anthropic API key (default: ANTHROPIC_API_KEY env var)

        Raises:
            AnswerGeneratorError: If initialization fails
        """
        if not Anthropic:
            raise AnswerGeneratorError("anthropic not installed")

        # Get API key from argument or environment
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not key:
            raise AnswerGeneratorError(
                "ANTHROPIC_API_KEY not provided and not in environment"
            )

        try:
            self.client = Anthropic(api_key=key)
        except Exception as e:
            raise AnswerGeneratorError(f"Failed to initialize Claude client: {str(e)}")

    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        max_tokens: Optional[int] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate answer using Claude API with RAG context.

        Args:
            question: User's question
            context_chunks: List of context chunks from RAGRetriever
            max_tokens: Maximum tokens in response (default: 1024)

        Returns:
            Tuple of (answer_text, citations)

        Raises:
            AnswerGeneratorError: If generation fails
        """
        if not question or len(question.strip()) == 0:
            raise AnswerGeneratorError("Question cannot be empty")

        if not context_chunks:
            raise AnswerGeneratorError("Context chunks required for RAG")

        max_tokens = max_tokens or self.MAX_TOKENS

        try:
            # Step 1: Format context for prompt
            context_string = self._format_context(context_chunks)

            # Step 2: Build RAG prompt
            prompt = self.RAG_PROMPT_TEMPLATE.format(
                context=context_string,
                question=question
            )

            # Step 3: Call Claude API
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=max_tokens,
                temperature=self.TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Step 4: Extract answer text
            answer_text = response.content[0].text.strip()

            # Step 5: Extract citations from answer
            citations = self._extract_citations(answer_text, context_chunks)

            return answer_text, citations

        except Exception as e:
            raise AnswerGeneratorError(f"Failed to generate answer: {str(e)}")

    def _format_context(
        self,
        context_chunks: List[Dict[str, Any]],
        separator: str = "\n---\n"
    ) -> str:
        """
        Format context chunks for prompt injection.

        Args:
            context_chunks: List of context chunks
            separator: Separator between chunks

        Returns:
            Formatted context string
        """
        context_parts = []

        for chunk in context_chunks:
            rank = chunk.get('rank', 0)
            text = chunk.get('chunk_text', '')
            score = chunk.get('similarity_score', 0.0)

            # Format: [Source #1 (score: 0.92)] chunk text...
            header = f"[Source #{rank} (relevance: {score:.2f})]"
            context_parts.append(f"{header}\n{text}")

        return separator.join(context_parts)

    def _extract_citations(
        self,
        answer_text: str,
        context_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from generated answer.

        Args:
            answer_text: Generated answer text
            context_chunks: Original context chunks used

        Returns:
            List of citations with source info

        Raises:
            AnswerGeneratorError: If extraction fails
        """
        citations = []

        try:
            # Pattern 1: Match [Source #N] patterns in answer
            source_pattern = r'\[Source\s*#(\d+)\]'
            source_matches = re.findall(source_pattern, answer_text)

            # Track unique citations by source number
            cited_sources = set()
            for match in source_matches:
                source_num = int(match)
                if source_num not in cited_sources:
                    cited_sources.add(source_num)

            # Build citation list with original chunk text
            for source_num in sorted(cited_sources):
                # Find matching chunk (rank is 1-indexed)
                matching_chunk = None
                for chunk in context_chunks:
                    if chunk.get('rank') == source_num:
                        matching_chunk = chunk
                        break

                if matching_chunk:
                    citation = {
                        'source_rank': source_num,
                        'chunk_text': matching_chunk.get('chunk_text', ''),
                        'similarity_score': matching_chunk.get('similarity_score', 0.0),
                        'chunk_size': matching_chunk.get('chunk_size', 0)
                    }
                    citations.append(citation)

            # Pattern 2: If no explicit citations, mark all context as implicit sources
            if not citations and context_chunks:
                # Use top chunk as implicit source
                top_chunk = context_chunks[0]
                citations.append({
                    'source_rank': top_chunk.get('rank', 1),
                    'chunk_text': top_chunk.get('chunk_text', ''),
                    'similarity_score': top_chunk.get('similarity_score', 0.0),
                    'chunk_size': top_chunk.get('chunk_size', 0),
                    'implicit': True
                })

            return citations

        except Exception as e:
            raise AnswerGeneratorError(f"Citation extraction failed: {str(e)}")

    def format_answer_with_citations(
        self,
        answer_text: str,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Format answer with citations for display.

        Args:
            answer_text: Generated answer
            citations: List of citations

        Returns:
            Formatted answer string with citations
        """
        if not citations:
            return answer_text

        formatted = answer_text + "\n\n## Sources\n"

        for i, citation in enumerate(citations, 1):
            source_rank = citation.get('source_rank', '?')
            score = citation.get('similarity_score', 0.0)
            text_preview = citation.get('chunk_text', '')[:100] + "..."

            formatted += f"\n[{i}] Source #{source_rank} (relevance: {score:.2f})\n"
            formatted += f"    {text_preview}\n"

        return formatted

    def validate_answer(
        self,
        answer_text: str
    ) -> Tuple[bool, str]:
        """
        Validate generated answer.

        Args:
            answer_text: Generated answer text

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not answer_text or len(answer_text.strip()) == 0:
            return False, "Empty answer generated"

        if len(answer_text) > 10000:
            return False, "Answer too long (>10000 chars)"

        if len(answer_text) < 20:
            return False, "Answer too short (<20 chars)"

        return True, ""
