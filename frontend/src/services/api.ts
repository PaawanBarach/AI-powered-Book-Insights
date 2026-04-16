import { Book, BookListItem, PaginatedResponse } from '../types'

const API_BASE = '/api'

export async function fetchBooks(params: {
  search?: string
  genre?: string
  page?: number
}): Promise<PaginatedResponse<BookListItem>> {
  const searchParams = new URLSearchParams()
  if (params.search) searchParams.set('search', params.search)
  if (params.genre) searchParams.set('genre', params.genre)
  if (params.page) searchParams.set('page', String(params.page))
  
  const res = await fetch(`${API_BASE}/books/?${searchParams}`)
  if (!res.ok) throw new Error('Failed to fetch books')
  return res.json()
}

export async function fetchBook(id: number): Promise<Book> {
  const res = await fetch(`${API_BASE}/books/${id}/`)
  if (!res.ok) throw new Error('Failed to fetch book')
  return res.json()
}

export async function fetchRecommendations(id: number): Promise<BookListItem[]> {
  const res = await fetch(`${API_BASE}/books/${id}/recommendations/`)
  if (!res.ok) throw new Error('Failed to fetch recommendations')
  return res.json()
}

export async function askQuestion(question: string, sessionId?: string) {
  const body: { question: string; session_id?: string } = { question }
  if (sessionId) body.session_id = sessionId
  
  const res = await fetch(`${API_BASE}/qa/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error('Failed to ask question')
  return res.json()
}

export async function fetchChat(sessionId: string) {
  const res = await fetch(`${API_BASE}/chat/${sessionId}/`)
  if (!res.ok) throw new Error('Failed to fetch chat')
  return res.json()
}