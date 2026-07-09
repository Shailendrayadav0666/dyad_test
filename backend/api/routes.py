"""API Routes - FastAPI."""

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.components.pdf_processor import PDFProcessor, InvalidPDFError, FileReadError
from backend.components.session_manager import SessionManager
from backend.components.embedding_engine import EmbeddingEngine, EmbeddingError
from backend.components.vector_store import VectorStore, VectorStoreError
from backend.components.rag_retriever import RAGRetriever, RAGRetrieverError
from backend.components.answer_generator import AnswerGenerator, AnswerGeneratorError
from backend.utils.file_wrapper import UploadFileWrapper

# Singleton components (in-memory, ephemeral)
pdf_processor = PDFProcessor()
session_manager = SessionManager()
embedding_engine = EmbeddingEngine()
vector_store = VectorStore()
rag_retriever = RAGRetriever(embedding_engine)

try:
    answer_generator = AnswerGenerator()
except AnswerGeneratorError:
    answer_generator = None

router = APIRouter()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def err(status: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={'error': error, 'message': message})


class QueryBody(BaseModel):
    session_id: str
    query: str


@router.post('/upload')
async def upload_pdf(file: UploadFile = File(...)):
    try:
        safe_name = Path(file.filename or '').name
        if not safe_name:
            return err(400, 'empty_filename', 'No file selected')
        if not allowed_file(safe_name):
            return err(400, 'invalid_file_type', 'Only PDF files are allowed')

        content = await file.read()
        wrapped = UploadFileWrapper(content, safe_name)

        try:
            pdf_processor.validate(wrapped)
        except InvalidPDFError as e:
            return err(400, 'invalid_pdf', str(e))

        try:
            extracted_text = pdf_processor.extract_text(wrapped)
        except FileReadError as e:
            return err(500, 'extraction_failed', str(e))

        wrapped.seek(0)
        pdf_metadata = pdf_processor.get_metadata(wrapped)
        pdf_metadata['upload_timestamp'] = datetime.utcnow().isoformat()

        session_id = session_manager.create_session(pdf_metadata)
        session_manager.store_session_data(session_id, {'pdf_text': extracted_text})

        try:
            embeddings_data = embedding_engine.process(extracted_text)
            embeddings_list = [
                {'chunk': chunk, 'vector': vector,
                 'chunk_size': len(chunk), 'embedding_dim': len(vector)}
                for chunk, vector in embeddings_data
            ]
            session_manager.store_session_data(session_id, {'embeddings': embeddings_list})
            pdf_metadata['chunks_generated'] = len(embeddings_list)
            pdf_metadata['embedding_dimension'] = embedding_engine.get_embedding_dimension()
        except EmbeddingError as e:
            return err(500, 'embedding_failed', str(e))

        try:
            collection_name = f'session_{session_id}'
            vector_store.create_collection(collection_name)
            points_stored = vector_store.store_embeddings(collection_name, embeddings_data)
            vector_store.get_collection_info(collection_name)
            session_manager.store_session_data(session_id, {'vector_store': collection_name})
            pdf_metadata['vectors_stored'] = points_stored
        except VectorStoreError as e:
            return err(500, 'vector_store_failed', str(e))

        return {
            'session_id': session_id,
            'status': 'ready',
            'message': 'PDF uploaded and processed successfully',
            'pdf_info': {
                'filename': pdf_metadata.get('filename', 'document.pdf'),
                'pages': pdf_metadata.get('page_count', 0),
                'file_size': pdf_metadata.get('file_size', 0),
                'extracted_characters': len(extracted_text),
            },
        }

    except Exception as e:
        return err(500, 'server_error', f'Unexpected error: {str(e)}')


@router.get('/status/{session_id}')
async def get_status(session_id: str):
    try:
        session = session_manager.get_session(session_id)
        return {
            'session_id': session_id,
            'status': 'ready',
            'created_at': session.get('created_at'),
            'last_activity': session.get('last_activity'),
            'pdf_info': session.get('pdf_metadata', {}),
        }
    except Exception:
        return JSONResponse(
            status_code=404,
            content={'error': 'session_not_found', 'message': f'Session {session_id} not found'},
        )


@router.post('/query')
async def query(body: QueryBody):
    try:
        if not body.query.strip():
            return err(400, 'empty_query', 'Query cannot be empty')
        if len(body.query) > 500:
            return err(400, 'query_too_long', 'Query must be ≤500 characters')

        try:
            session = session_manager.get_session(body.session_id)
        except Exception:
            return err(404, 'session_not_found', f'Session {body.session_id} not found')

        collection_name = session.get('vector_store')
        if not collection_name:
            return err(400, 'no_embeddings', 'Session has no embeddings. Upload a PDF first.')

        try:
            context_chunks = rag_retriever.retrieve_context(
                query=body.query,
                vector_store=vector_store,
                collection_name=collection_name,
                top_k=5,
            )
            context_string = rag_retriever.get_context_string(context_chunks)
            session['query_history'].append({
                'query': body.query,
                'timestamp': datetime.utcnow().isoformat(),
                'context_chunks': len(context_chunks),
            })
            return {
                'session_id': body.session_id,
                'query': body.query,
                'status': 'success',
                'context_chunks': context_chunks,
                'context_string': context_string,
                'chunks_retrieved': len(context_chunks),
            }
        except RAGRetrieverError as e:
            return err(500, 'retrieval_failed', str(e))

    except Exception as e:
        return err(500, 'server_error', f'Unexpected error: {str(e)}')


@router.post('/answer')
async def answer(body: QueryBody):
    try:
        if not answer_generator:
            return err(500, 'api_key_missing', 'ANTHROPIC_API_KEY environment variable not set')

        if not body.query.strip():
            return err(400, 'empty_query', 'Query cannot be empty')

        try:
            session = session_manager.get_session(body.session_id)
        except Exception:
            return err(404, 'session_not_found', f'Session {body.session_id} not found')

        collection_name = session.get('vector_store')
        if not collection_name:
            return err(400, 'no_embeddings', 'Session has no embeddings. Upload a PDF first.')

        try:
            context_chunks = rag_retriever.retrieve_context(
                query=body.query,
                vector_store=vector_store,
                collection_name=collection_name,
                top_k=5,
            )
            if not context_chunks:
                return err(400, 'no_context', 'No relevant content found for query')
        except RAGRetrieverError as e:
            return err(500, 'retrieval_failed', str(e))

        try:
            answer_text, citations = answer_generator.generate_answer(
                question=body.query,
                context_chunks=context_chunks,
            )
            is_valid, error_msg = answer_generator.validate_answer(answer_text)
            if not is_valid:
                return err(500, 'invalid_answer', f'Answer validation failed: {error_msg}')

            formatted_answer = answer_generator.format_answer_with_citations(answer_text, citations)
            session['query_history'].append({
                'query': body.query,
                'timestamp': datetime.utcnow().isoformat(),
                'has_answer': True,
            })

            return {
                'session_id': body.session_id,
                'query': body.query,
                'status': 'success',
                'answer': answer_text,
                'answer_with_sources': formatted_answer,
                'citations': citations,
                'context_chunks': context_chunks,
                'chunks_used': len(context_chunks),
            }
        except AnswerGeneratorError as e:
            return err(500, 'answer_generation_failed', str(e))

    except Exception as e:
        return err(500, 'server_error', f'Unexpected error: {str(e)}')
