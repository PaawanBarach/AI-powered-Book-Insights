from rest_framework import serializers
from .models import Book, BookChunk, ChatSession, ChatMessage


class BookChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookChunk
        fields = ['id', 'chunk_text', 'chunk_index']


class BookSerializer(serializers.ModelSerializer):
    subjects_list = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'book_url', 'cover_url',
            'publish_year', 'first_publish_year', 'number_of_pages',
            'rating_average', 'rating_count',
            'subjects', 'subjects_list',
            'olid', 'isbn_10', 'isbn_13',
            'ai_summary', 'ai_sentiment', 'ai_sentiment_score',
            'created_at', 'updated_at',
        ]

    def get_subjects_list(self, obj):
        return obj.get_subjects_list()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['has_embeddings'] = bool(instance.chunks.exists())
        return data


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'cover_url', 'rating_average', 'subjects']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'sources', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'messages', 'created_at']


class QASerializer(serializers.Serializer):
    question = serializers.CharField()
    session_id = serializers.CharField(required=False)