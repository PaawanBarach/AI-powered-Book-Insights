# Features

## Core Features

### Data Collection
- Selenium scraper targeting Open Library (openlibrary.org) — a real dynamic React-rendered site
- Extracts title, author, description, cover image, ratings, genre/subjects, book URL
- Handles missing fields gracefully, skips on error, logs progress

### Backend API (Django REST Framework)
- `GET /api/books/` — paginated book listing with search and genre filter
- `GET /api/books/:id/` — full book detail
- `GET /api/books/:id/recommendations/` — 5 related books by genre
- `POST /api/qa/` — ask a question, get an AI answer with cited sources
- `GET /api/chat/:session_id/` — retrieve chat history for a session

### Vector Search (ChromaDB + Sentence Transformers)
- Book descriptions chunked and embedded using all-MiniLM-L6-v2 (local, free)
- Stored in ChromaDB persistent vector store
- Semantic similarity search — finds relevant books by meaning, not just keywords

### RAG Pipeline
- User question → embedded → similarity search → top 5 chunks retrieved
- Context passed to Groq LLM (Llama 3 8B) with source-citation instruction
- Answer returned with list of book titles cited
- Responses cached by question hash to avoid redundant API calls

### AI Insights (Groq LLM)
- Summary: 2-sentence AI-generated summary per book from description
- Genre Classification: Single genre label predicted from title + description
- Sentiment Analysis: Positive / Mixed / Negative tone with score (0.0-1.0)
- Run via Django management command after scraping

### Chat History
- Each Q&A session has a UUID-based session ID
- Messages (user + assistant) stored in MySQL with timestamps
- Sources cited per assistant message stored as JSON
- Frontend loads and displays previous messages on session resume

## Bonus Features

- Response Caching: Identical questions return cached answers instantly
- Skeleton Loaders: All 3 pages show shimmer placeholders while data loads
- Cover Images: Real book cover images from Open Library CDN
- Error Handling: Graceful fallbacks on scrape failures, API errors, missing fields
