# Backend - Django REST API

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your database and API credentials

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Commands

```bash
# Scrape books from Open Library
python manage.py scrape_books

# Generate AI insights (summaries, genres, sentiment)
python manage.py generate_insights

# Run tests
python manage.py test

# Run specific test
python manage.py test books.tests.BookModelTest.test_book_creation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List books (paginated, searchable) |
| GET | `/api/books/{id}/` | Book detail |
| GET | `/api/books/{id}/recommendations/` | Related books |
| POST | `/api/qa/` | Ask AI a question |
| GET | `/api/chat/{session_id}/` | Chat history |

## Database Models

- **Book** - title, author, description, cover, ratings, AI insights
- **BookChunk** - chunked descriptions with embeddings
- **ChatSession** - user Q&A sessions
- **ChatMessage** - individual messages with sources

## Environment Variables

```
DATABASE_NAME=book_insight
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
GROQ_API_KEY=your_key_here
```

See `docs/AGENTS.md` for code style guidelines.
