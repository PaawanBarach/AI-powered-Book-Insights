# Book Insight Explorer

## Core Idea

Most book discovery tools show you what's popular. This shows you what's relevant — to your question, your mood, your current read.

You scrape real book data from Open Library, store it in a relational database, chunk and embed the descriptions into a vector store, and wire it all into a RAG pipeline. Ask "what should I read after Dune?" and the system doesn't keyword-match — it finds semantically similar books, pulls the most relevant chunks, and sends them as context to an LLM that answers with citations.

## Problem It Solves

Generic recommendation engines recommend based on popularity. They don't answer open-ended questions about themes, tone, or "books like X but darker." A RAG pipeline over a curated book dataset does.

## Architecture

```
Open Library (dynamic site)
        ↓ Selenium scraper
    MySQL Database
    Book | BookChunk | ChatSession | ChatMessage
        ↓ sentence-transformers (all-MiniLM-L6-v2)
    ChromaDB (vector store)
        ↓ similarity search
    Groq API (Llama 3 8B)
        ↓ answer + citations
    Django REST Framework
        ↓ JSON API
    React + Tailwind Frontend
    Book List | Book Detail | Q&A Chat
```

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Scraping | Selenium | Open Library is React-rendered, needs real browser |
| Backend | Django REST Framework | Required by assignment |
| Relational DB | MySQL | Required by assignment |
| Vector DB | ChromaDB | Simpler than FAISS, persistent, well-documented |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | Free, local, fast |
| LLM | Groq API Llama 3 8B | Free tier, fast inference, no GPU needed |
| Frontend | React + Tailwind CSS | Required by assignment |

## Database Models

### Book
title, author, year, description, cover_url, rating, num_ratings,
genre, sentiment, sentiment_score, ai_summary, book_url, created_at

### BookChunk
book (FK), chunk_text, chunk_index, embedding_id

### ChatSession
session_id (UUID), created_at

### ChatMessage
session (FK), role (user/assistant), content, sources (JSON), created_at

## Data Flow

1. Scrape: Selenium loads Open Library, extracts 200+ books, saves to MySQL
2. Embed: Chunk descriptions, generate embeddings, load into ChromaDB
3. Insights: Groq generates summaries, genres, sentiment per book
4. Query: User asks → embedded → ChromaDB top 5 → Groq answers → cached + saved
5. Display: React fetches from Django REST API
