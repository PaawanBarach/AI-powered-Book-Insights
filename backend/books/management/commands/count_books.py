from django.core.management.base import BaseCommand
from books.models import Book
from django.db.models import Count

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = Book.objects.values('subjects').annotate(count=Count('id')).order_by('-count')
        for r in results:
            self.stdout.write(f'{r["subjects"]:20} {r["count"]}')
        self.stdout.write(f'Total: {Book.objects.count()}')