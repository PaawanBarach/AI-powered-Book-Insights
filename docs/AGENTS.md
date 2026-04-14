# AGENTS.md - Book Insight Explorer

> Agentic coding guidelines for this repository. AI agents should follow these conventions.

## Project Overview

Book Insight Explorer is a RAG-powered book recommendation system. It scrapes books from Open Library, stores them in MySQL, embeds descriptions into ChromaDB, and uses Groq LLM to answer natural language questions with citations.

**Tech Stack:**
- Backend: Django REST Framework (Python)
- Frontend: React + Tailwind CSS
- Database: MySQL (relational) + ChromaDB (vector store)
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- LLM: Groq API (Llama 3 8B)
- Scraper: Selenium

---

## Build / Lint / Test Commands

### Python / Django Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run Django development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Run a single test
python manage.py test books.tests.BookModelTest.test_book_creation

# Run all tests
python manage.py test

# Run pytest (if configured)
pytest

# Run a specific pytest test
pytest books/tests/test_models.py::BookModelTest::test_book_creation -v

# Lint with flake8
flake8 .

# Lint with ruff (faster)
ruff check .

# Format code with black
black .

# Sort imports with isort
isort --profile=black .
```

### React Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Run a specific test
npm test -- --testPathPattern="BookList" --watchAll=false

# Run tests in watch mode
npm test

# Format with Prettier
npx prettier --write src/
```

### Scraper

```bash
# Run the book scraper
python manage.py scrape_books

# Generate AI insights (summaries, genres, sentiment)
python manage.py generate_insights
```

---

## Code Style Guidelines

### Python / Django

#### Imports
- Standard library first, then third-party, then local
- Use isort to automate: `isort --profile=black .`
- Never use `import *`
- Relative imports for internal modules

```python
# Correct
import os
import sys
from pathlib import Path

import django
from django.db import models
from rest_framework import serializers

from .models import Book
from .tasks import scrape_books

# Incorrect
from django.db import *  # Never wildcard imports
```

#### Formatting
- Use Black with line length 88 (default)
- 4 spaces for indentation (no tabs)
- One blank line between top-level definitions
- Two blank lines between class definitions

```python
# Good
class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)

    class Meta:
        ordering = ["-created_at"]


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chunk_text = models.TextField()
```

#### Type Hints
- Always use type hints for function signatures
- Use `typing` module for complex types
- Prefer `list[str]` over `List[str]` (Python 3.9+)

```python
# Good
def get_book_by_id(book_id: int) -> Book | None:
    """Fetch a book by its ID."""
    try:
        return Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return None


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into chunks of specified size."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
```

#### Naming Conventions
- Classes: `PascalCase` (e.g., `BookSerializer`)
- Functions/methods: `snake_case` (e.g., `get_or_create_session`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_CHUNK_SIZE`)
- Variables: `snake_case` (e.g., `book_instance`)
- Boolean variables: prefix with `is_`, `has_`, `should_` (e.g., `is_active`)

```python
# Good
class BookSerializer(serializers.ModelSerializer):
    MAX_TITLE_LENGTH = 500  # Constant

    def to_representation(self, instance: Book) -> dict:
        is_available = instance.cover_url is not None
        return {"title": instance.title, "has_cover": is_available}
```

#### Error Handling
- Use specific exceptions (`Book.DoesNotExist`, not generic `Exception`)
- Always log errors before re-raising
- Return `None` or default values for expected failures
- Use custom exception classes for domain errors

```python
# Good
import logging

logger = logging.getLogger(__name__)


class BookNotFoundError(Exception):
    """Raised when a requested book does not exist."""
    pass


def get_book(book_id: int) -> Book:
    """Retrieve a book or raise an error."""
    try:
        return Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        logger.error(f"Book with id {book_id} not found")
        raise BookNotFoundError(f"Book {book_id} not found")
```

---

### React / JavaScript

#### Imports
- React imports first, then third-party, then local
- Use absolute imports when configured (via tsconfig/jsconfig)
- Named imports for React components

```javascript
// Good
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import BookCard from "./components/BookCard";

// Good - absolute import
import { API_ENDPOINTS } from "config";
```

#### Formatting
- Use Prettier with default settings
- 2 spaces for indentation
- Single quotes for strings
- Trailing commas in objects/arrays
- Semicolons statement-ending

#### TypeScript (if used)
- Prefer interfaces for objects, types for unions
- Use `enum` sparingly (prefer const objects)
- Never use `any`

```typescript
// Good
interface Book {
  id: number;
  title: string;
  author: string;
  coverUrl?: string;
}

type BookWithRating = Book & {
  rating: number;
};

// Good - function types
function fetchBook(id: number): Promise<Book> {
  return api.get(`/books/${id}`).then((res) => res.data);
}
```

#### Component Patterns
- Use functional components with hooks
- Extract custom hooks for reusable logic
- Keep components small and focused
- Use TypeScript interfaces for props

```typescript
// Good
interface BookCardProps {
  book: Book;
  onSelect?: (book: Book) => void;
}

export function BookCard({ book, onSelect }: BookCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = () => {
    onSelect?.(book);
  };

  return (
    <div className="book-card" onClick={handleClick}>
      <img src={book.coverUrl} alt={book.title} />
    </div>
  );
}
```

---

### General Best Practices

1. **Never commit secrets** - Use environment variables, never hardcode API keys
2. **Keep functions small** - One responsibility per function (SRP)
3. **Write tests first** - Test-driven development for new features
4. **Document complex logic** - Docstrings for non-obvious code
5. **Use meaningful names** - Avoid single-letter variables except loops
6. **Handle edge cases** - Empty collections, null values, network failures
7. **Log appropriately** - Debug for development, info for important events, error for failures

---

### Database Queries

- Use Django ORM QuerySet methods (filter, exclude, get)
- Select related fields to avoid N+1 queries
- Use `.values()` or `.values_list()` for read-only data
- Never use raw SQL unless absolutely required

```python
# Good - select_related avoids N+1
books = Book.objects.select_related("genre").filter(is_active=True)

# Good - values for read-only
book_titles = list(Book.objects.values_list("title", flat=True))

# Good - bulk operations
Book.objects.bulk_create(new_books, ignore_conflicts=True)
```

---

### API Design

- Use RESTful conventions: `/api/resource/`
- POST for creation, GET for retrieval, PUT/PATCH for update, DELETE for deletion
- Return appropriate status codes (200, 201, 204, 400, 404, 500)
- Use pagination for list endpoints
- Version APIs: `/api/v1/`

```python
# Good - Django REST Framework
class BookListView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_class = BookFilter
    pagination_class = PageNumberPagination
```

---

### Testing Guidelines

- Use `pytest` for Python (with pytest-django)
- Use `jest` or `vitest` for React
- Test edge cases, not just happy paths
- Mock external services (API calls, file I/O)
- Use factories (Factory Boy) for test data

```python
# Good - pytest
@pytest.fixture
def sample_book():
    return BookFactory(title="Dune", author="Frank Herbert")


def test_book_str(sample_book):
    assert str(sample_book) == "Dune by Frank Herbert"


def test_book_not_found():
    with pytest.raises(BookNotFoundError):
        get_book(9999)
```

---

### Git Conventions

- Use meaningful commit messages: `Add book search filtering` not `fix`
- Commit often: small, focused changes
- Use branches: `feature/book-search`, `fix/scraper-error`
- Pull before push to avoid conflicts
- Review diffs before committing