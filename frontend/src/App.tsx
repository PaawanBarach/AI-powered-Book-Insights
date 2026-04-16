import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BookList from './pages/BookList'
import BookDetail from './pages/BookDetail'
import { ChatModal } from './components/ChatModal'
import { AddBookModal } from './components/AddBookModal'

const queryClient = new QueryClient()

export default function App() {
  const [chatOpen, setChatOpen] = useState(false)
  const [addBookOpen, setAddBookOpen] = useState(false)

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white border-b border-gray-200">
            <div className="max-w-6xl mx-auto px-6 py-6 flex justify-between items-center">
              <Link to="/" className="text-2xl font-bold text-gray-900">
                Book Insight
              </Link>
              <div className="flex gap-4">
                <button
                  onClick={() => setChatOpen(true)}
                  className="px-6 py-3 bg-gray-900 text-white hover:bg-gray-800 text-base font-medium"
                >
                  Ask a Question
                </button>
                <button
                  onClick={() => setAddBookOpen(true)}
                  className="px-6 py-3 border-2 border-gray-900 text-gray-900 hover:bg-gray-50 text-base font-medium"
                >
                  Add Book
                </button>
              </div>
            </div>
          </nav>
          <main className="max-w-6xl mx-auto px-6 py-10">
            <Routes>
              <Route path="/" element={<BookList />} />
              <Route path="/books/:id" element={<BookDetail />} />
            </Routes>
          </main>
        </div>
        <ChatModal isOpen={chatOpen} onClose={() => setChatOpen(false)} />
        <AddBookModal isOpen={addBookOpen} onClose={() => setAddBookOpen(false)} />
      </BrowserRouter>
    </QueryClientProvider>
  )
}