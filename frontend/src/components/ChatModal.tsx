import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { askQuestion, fetchChat } from '../services/api'
import { ChatMessage } from '../types'

interface ChatModalProps {
  isOpen: boolean
  onClose: () => void
  bookId?: number
  bookTitle?: string
}

export function ChatModal({ isOpen, onClose, bookId, bookTitle }: ChatModalProps) {
  const { sessionId: urlSessionId } = useParams()
  const navigate = useNavigate()
  const [sessionId, setSessionId] = useState<string | undefined>(urlSessionId)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const qaMutation = useMutation({
    mutationFn: ({ q, sid }: { q: string; sid?: string }) => askQuestion(q, sid),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: 'user', content: question, sources: null, created_at: new Date().toISOString() },
        { id: Date.now() + 1, role: 'assistant', content: data.answer, sources: JSON.stringify(data.sources), created_at: new Date().toISOString() },
      ])
      setSessionId(data.session_id)
      if (bookId) navigate(`/books/${bookId}/?session=${data.session_id}`, { replace: true })
      setQuestion('')
    },
  })

  const loadChat = useCallback(async () => {
    if (!sessionId) return
    try {
      const data: any = await fetchChat(sessionId)
      setMessages(data.messages || [])
    } catch (err) {
      console.error('Failed to load chat:', err)
    }
  }, [sessionId])

  useEffect(() => {
    if (isOpen) {
      setSessionId(urlSessionId)
      if (urlSessionId) loadChat()
    }
  }, [isOpen, urlSessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, qaMutation.isPending])

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return
    const initialMsg = bookId ? `I'm looking for books similar to "${bookTitle}"` : question
    qaMutation.mutate({ q: initialMsg || question, sid: sessionId })
  }

  return (
    <div className="fixed inset-0 bg-gray-900/70 flex items-center justify-center z-50">
      <div className="bg-white w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">Ask about books</h2>
          <button onClick={onClose} className="text-3xl text-gray-400 hover:text-gray-600 leading-none">&times;</button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-[400px]">
          {messages.length === 0 && !qaMutation.isPending && (
            <p className="text-gray-500 text-center text-lg">
              Ask about books. E.g. "What should I read next?"
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`${msg.role === 'user' ? 'ml-auto bg-gray-100' : 'mr-auto bg-gray-50'} p-4`}>
              <p className="text-gray-800 whitespace-pre-wrap text-base">{msg.content}</p>
              {msg.sources && msg.role === 'assistant' && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-sm text-gray-600">
                  {JSON.parse(msg.sources).map((s: any, j: number) => (
                    <p key={j}>• {s.title}</p>
                  ))}
                </div>
              )}
            </div>
          ))}
          {qaMutation.isPending && (
            <div className="mr-auto bg-gray-50 p-4">
              <p className="text-gray-500 animate-pulse text-base">Thinking...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-6 border-t border-gray-200 flex gap-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about books..."
            disabled={qaMutation.isPending}
            className="flex-1 px-4 py-3 border border-gray-300 text-base focus:border-gray-400 focus:ring-0 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={qaMutation.isPending || !question.trim()}
            className="px-8 py-3 bg-gray-900 text-white text-base font-medium hover:bg-gray-800 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}