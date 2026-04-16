import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from books.models import Book, BookChunk

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate embeddings for book descriptions and store in ChromaDB'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, default=100)

    def handle(self, *args, **options):
        batch_size = options['batch']
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
        collection = chroma_client.get_or_create_collection('book_descriptions')

        books = Book.objects.filter(description__isnull=False).exclude(description='')
        total = books.count()
        self.stdout.write(f'Embedding {total} books...')

        for i in range(0, total, batch_size):
            batch = list(books[i:i + batch_size])
            texts = []
            ids = []
            metadatas = []

            for book in batch:
                text = f"{book.title}. {book.author or ''}. {book.description or ''}"
                texts.append(text)
                ids.append(f"book_{book.id}")
                metadatas.append({
                    'book_id': book.id,
                    'title': book.title,
                    'author': book.author or '',
                })

            embeddings = model.encode(texts, show_progress_bar=False)
            
            collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )

            BookChunk.objects.filter(book__in=batch).delete()
            for j, book in enumerate(batch):
                for k in range(len(texts)):
                    if metadatas[k]['book_id'] == book.id:
                        BookChunk.objects.create(
                            book=book,
                            chunk_text=texts[k][:1000],
                            chunk_index=0,
                            chroma_id=ids[k]
                        )

            self.stdout.write(f'Embedded {min(i + batch_size, total)}/{total}')
        
        self.stdout.write(self.style.SUCCESS(f'Done! {total} books embedded'))