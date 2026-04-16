import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


@receiver(post_save, sender='books.Book')
def book_saved(sender, instance, created, **kwargs):
    if not instance.description:
        return
    
    try:
        import chromadb
        from django.conf import settings
        
        collection = chromadb.PersistentClient(
            path=str(settings.CHROMA_PERSIST_DIR)
        ).get_or_create_collection('book_descriptions')
        
        text = f"{instance.title} by {instance.author or 'Unknown'}. {instance.description}"
        embedding = get_embedding_model().encode([text], convert_to_numpy=True)[0].tolist()
        
        collection.upsert(
            ids=[str(instance.id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                'book_id': instance.id,
                'title': instance.title,
                'author': instance.author or '',
                'subjects': instance.subjects or '',
            }]
        )
        logger.info(f'Auto-vectorized: {instance.id}')
    except Exception as e:
        logger.error(f'vectorize failed {instance.id}: {e}')


@receiver(post_delete, sender='books.Book')
def book_deleted(sender, instance, **kwargs):
    try:
        import chromadb
        from django.conf import settings
        
        collection = chromadb.PersistentClient(
            path=str(settings.CHROMA_PERSIST_DIR)
        ).get_or_create_collection('book_descriptions')
        collection.delete(ids=[str(instance.id)])
    except Exception as e:
        logger.error(f'delete failed {instance.id}: {e}')