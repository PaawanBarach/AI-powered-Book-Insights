import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from groq import Groq

from books.models import Book

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate AI summaries for books using Groq'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, default=50)

    def handle(self, *args, **options):
        batch_size = options['batch']
        
        if not settings.GROQ_API_KEY:
            self.stdout.write('Error: GROQ_API_KEY not set')
            return

        client = Groq(api_key=settings.GROQ_API_KEY)

        books = Book.objects.filter(description__isnull=False).exclude(description='').filter(ai_summary__isnull=True)
        total = books.count()
        self.stdout.write(f'Generating summaries for {total} books...')

        for i in range(0, total, batch_size):
            batch = list(books[i:i + batch_size])
            
            for book in batch:
                try:
                    prompt = f"""Write a brief 2-sentence summary of this book:
Title: {book.title}
By: {book.author or 'Unknown'}
Description: {book.description[:800]}"""

                    response = client.chat.completions.create(
                        model='llama-3-8b-8192',
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=0.5,
                    )

                    summary = response.choices[0].message.content.strip()
                    book.ai_summary = summary[:500]
                    book.save()

                    self.stdout.write(f'{book.title[:30]}...')
                    
                except Exception as e:
                    logger.error(f'Error: {e}')

            self.stdout.write(f'Done {min(i + batch_size, total)}/{total}')

        self.stdout.write(self.style.SUCCESS('All done!'))