from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    book_url = models.URLField(max_length=500, unique=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)

    publish_year = models.PositiveIntegerField(blank=True, null=True)
    first_publish_year = models.PositiveIntegerField(blank=True, null=True)
    number_of_pages = models.PositiveIntegerField(blank=True, null=True)

    rating_average = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    rating_count = models.PositiveIntegerField(blank=True, null=True)

    subjects = models.TextField(blank=True, null=True)
    subject_places = models.TextField(blank=True, null=True)
    subject_times = models.TextField(blank=True, null=True)
    subject_people = models.TextField(blank=True, null=True)

    olid = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    ol_edition_id = models.CharField(max_length=20, blank=True, null=True)
    ol_work_id = models.CharField(max_length=20, blank=True, null=True)

    isbn_10 = models.CharField(max_length=10, blank=True, null=True)
    isbn_13 = models.CharField(max_length=13, blank=True, null=True)
    preview_url = models.URLField(max_length=500, blank=True, null=True)

    ai_summary = models.TextField(blank=True, null=True)
    ai_sentiment = models.CharField(
        max_length=20, blank=True, null=True,
        choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')]
    )
    ai_sentiment_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['olid']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"

    def get_subjects_list(self):
        if not self.subjects:
            return []
        return [s.strip() for s in self.subjects.split(',')]


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    chunk_index = models.PositiveIntegerField()
    chroma_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['book', 'chunk_index']
        unique_together = ['book', 'chunk_index']

    def __str__(self):
        return f"{self.book.title} - Chunk {self.chunk_index}"


class ChatSession(models.Model):
    session_id = models.CharField(max_length=36, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id}"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    sources = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."