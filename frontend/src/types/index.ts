export interface Book {
  id: number
  title: string
  author: string | null
  description: string | null
  book_url: string
  cover_url: string | null
  publish_year: number | null
  first_publish_year: number | null
  number_of_pages: number | null
  rating_average: string | null
  rating_count: number | null
  subjects: string | null
  subjects_list: string[]
  olid: string | null
  isbn_10: string | null
  isbn_13: string | null
  ai_summary: string | null
  ai_sentiment: string | null
  ai_sentiment_score: string | null
  has_embeddings: boolean
  created_at: string
  updated_at: string
}

export interface BookListItem {
  id: number
  title: string
  author: string | null
  description: string | null
  cover_url: string | null
  rating_average: string | null
  subjects: string | null
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources: string | null
  created_at: string
}

export interface ChatSession {
  id: number
  session_id: string
  messages: ChatMessage[]
  created_at: string
}

export interface QARequest {
  question: string
  session_id?: string
}

export interface QAResponse {
  answer: string
  session_id: string
  sources: Source[]
}

export interface Source {
  title: string
  book_id: number
  chunk: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}