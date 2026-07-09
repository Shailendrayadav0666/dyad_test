"""Session Manager Component - Handles session lifecycle and in-memory state."""

import uuid
from datetime import datetime
from typing import Dict, Any


class SessionNotFoundError(Exception):
    """Raised when session is not found."""
    pass


class SessionManager:
    """Manages user sessions in-memory (ephemeral)."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, pdf_metadata: Dict[str, Any]) -> str:
        """
        Create a new session for a PDF document.

        Args:
            pdf_metadata: PDF metadata (filename, page_count, etc.)

        Returns:
            session_id (UUID string)
        """
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'pdf_metadata': pdf_metadata,
            'pdf_text': '',
            'embeddings': [],
            'vector_store': None,
            'query_history': []
        }

        return session_id

    def store_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Store session data (PDF text, embeddings, etc.).

        Args:
            session_id: Session identifier
            data: Dictionary with keys like 'pdf_text', 'embeddings', etc.

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        if session_id not in self.sessions:
            raise SessionNotFoundError(f"Session {session_id} not found")

        for key, value in data.items():
            if key in self.sessions[session_id]:
                self.sessions[session_id][key] = value

        self.sessions[session_id]['last_activity'] = datetime.utcnow().isoformat()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        if session_id not in self.sessions:
            raise SessionNotFoundError(f"Session {session_id} not found")

        # Update last_activity
        self.sessions[session_id]['last_activity'] = datetime.utcnow().isoformat()

        return self.sessions[session_id]

