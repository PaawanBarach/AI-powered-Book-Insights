from django.core.management.base import BaseCommand
from books.models import Book

class Command(BaseCommand):
    def handle(self, *args, **options):
        total = Book.objects.count()
        with_desc = Book.objects.exclude(description__isnull=True).exclude(description='').count()
        with_author = Book.objects.exclude(author__isnull=True).exclude(author='').count()
        with_rating = Book.objects.exclude(rating_average__isnull=True).count()
        self.stdout.write(f'Total: {total}')
        self.stdout.write(f'With description: {with_desc}')
        self.stdout.write(f'With author: {with_author}')
        self.stdout.write(f'With rating: {with_rating}')