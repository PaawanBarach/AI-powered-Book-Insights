import os
import uuid
import json
import hashlib
import logging

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Q

from .models import Book, BookChunk, ChatSession, ChatMessage
from .serializers import (
    BookSerializer, BookListSerializer, BookChunkSerializer,
    ChatSessionSerializer, QASerializer
)

logger = logging.getLogger(__name__)

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    from groq import Groq
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'subjects']
    ordering_fields = ['title', 'created_at', 'rating_average']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        genre = self.request.query_params.get('genre')
        if genre:
            genre_normalized = genre.replace(' ', '_').lower()
            queryset = queryset.filter(subjects__icontains=genre_normalized)
        
        search = self.request.query_params.get('search')
        if search and not genre:
            try:
                results = search_similar_books(search, top_k=50)
                if results and results.get('ids') and results['ids'][0]:
                    similar_ids = [int(id_) for id_ in results['ids'][0]]
                    queryset = Book.objects.filter(pk__in=similar_ids)
            except Exception as e:
                logger.error(f'Vector search failed, fallback to text: {e}')
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(author__icontains=search) |
                    Q(subjects__icontains=search)
                )
        elif search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(subjects__icontains=search)
            )
        return queryset

    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        book = self.get_object()
        similar = Book.objects.filter(subjects=book.subjects).exclude(pk=book.pk)[:5]
        serializer = BookListSerializer(similar, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        book = self.get_object()
        chunks = book.chunks.all()
        serializer = BookChunkSerializer(chunks, many=True)
        return Response(serializer.data)


def get_embedding_model():
    if not hasattr(get_embedding_model, '_model'):
        get_embedding_model._model = SentenceTransformer('all-MiniLM-L6-v2')
    return get_embedding_model._model


def search_similar_books(query, top_k=5):
    client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection('book_descriptions')
    
    model = get_embedding_model()
    query_embedding = model.encode([query], convert_to_numpy=True)[0].tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results


def generate_answer(question, context_books):
    if not settings.GROQ_API_KEY:
        return "GROQ_API_KEY not configured", []
    
    cache_key = hashlib.md5(question.encode()).hexdigest()
    cache_dir = settings.BASE_DIR / 'qa_cache'
    cache_file = cache_dir / f'{cache_key}.json'
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                logger.info(f'Cache hit for question: {question[:50]}...')
                return cached['answer'], cached['sources']
        except Exception:
            pass
    
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    context = "\n\n".join([
        f"Book: {b.get('title', '')}\nDescription: {b.get('chunk', '')}"
        for b in context_books[:5]
    ])
    
    prompt = f"""You are a book recommendation assistant. Answer the user's question based ONLY on the book descriptions provided below.

Books:
{context}

User Question: {question}

Instructions:
- Answer directly based on the book descriptions provided
- If recommending books, mention specific titles from the context
- If you don't have enough information, say so
- Keep answer concise (2-4 sentences)"""

    try:
        response = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.5,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        
        cache_dir.mkdir(exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({'answer': answer, 'sources': context_books}, f)
        
        return answer, context_books
    except Exception as e:
        logger.error(f'Groq error: {e}')
        return f"Error generating answer: {str(e)}", []


class QAViewSet(viewsets.ViewSet):
    def create(self, request):
        if not RAG_AVAILABLE:
            return Response(
                {'error': 'RAG dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = QASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id')
        
        if not session_id:
            session_id = str(uuid.uuid4())
            ChatSession.objects.create(session_id=session_id)
        
        session = ChatSession.objects.get(session_id=session_id)
        ChatMessage.objects.create(session=session, role='user', content=question)
        
        search_results = search_similar_books(question, top_k=5)
        
        sources = []
        if search_results.get('metadatas'):
            for i, meta in enumerate(search_results['metadatas'][0]):
                sources.append({
                    'title': meta.get('title', 'Unknown'),
                    'book_id': meta.get('book_id'),
                    'chunk': search_results['documents'][0][i][:300] if search_results.get('documents') else ''
                })
        
        answer, _ = generate_answer(question, sources)
        
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=answer,
            sources=json.dumps(sources)
        )
        
        return Response({
            'answer': answer,
            'session_id': session_id,
            'sources': sources
        }, status=status.HTTP_201_CREATED)


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    lookup_field = 'session_id'