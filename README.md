# Book Insight Explorer

A RAG-powered book recommendation system that answers natural language questions with cited sources.

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### Setup

1. **Backend**
   ```bash
   cd backend
   cp .env.example .env  # Configure your environment
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py scrape_books
   python manage.py runserver
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Visit `http://localhost:5173`

## Project Structure

```
├── backend/     # Django REST API
├── frontend/    # React + Tailwind
├── docs/        # Documentation
└── README.md    # This file
```

## Tech Stack

- **Backend:** Django, DRF, MySQL, ChromaDB
- **Frontend:** React, Tailwind CSS
- **AI:** Groq (Llama 3), sentence-transformers
- **Scraping:** Selenium

See `docs/AGENTS.md` for coding conventions.
