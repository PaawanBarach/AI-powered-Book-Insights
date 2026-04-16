import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchBook, fetchRecommendations } from '../services/api'
import { ChatModal } from '../components/ChatModal'

function SkeletonDetail() {
  return (
    <div className="animate-pulse">
      <div className="flex gap-8">
        <div className="w-48 aspect-[2/3] skeleton" />
        <div className="flex-1 space-y-4">
          <div className="h-8 skeleton w-3/4" />
          <div className="h-4 skeleton w-1/2" />
          <div className="h-4 skeleton w-1/4" />
        </div>
      </div>
    </div>
  )
}

export default function BookDetail() {
  const navigate = useNavigate()
  const { id } = useParams()
  const bookId = Number(id)
  const [chatOpen, setChatOpen] = useState(false)

  const { data: book, isLoading: bookLoading } = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => fetchBook(bookId),
    enabled: !!bookId,
  })

  const { data: recommendations, isLoading: recLoading } = useQuery({
    queryKey: ['recommendations', bookId],
    queryFn: () => fetchRecommendations(bookId),
    enabled: !!bookId,
  })

  if (bookLoading) return <SkeletonDetail />

  if (!book) return <p className="text-red-600">Book not found</p>

  return (
    <div>
      <button
        onClick={() => navigate(-1)}
        className="text-gray-600 hover:text-gray-900 mb-4"
      >
        ← Back
      </button>
      <div className="flex gap-8 mb-12">
        <div className="w-48 flex-shrink-0">
          {book.cover_url ? (
            <img
              src={book.cover_url}
              alt={book.title}
              className="w-full shadow-sm"
            />
          ) : (
            <div className="w-full aspect-[2/3] bg-gray-100 flex items-center justify-center text-gray-400">
              No Cover
            </div>
          )}
        </div>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{book.title}</h1>
          <p className="text-lg text-gray-600 mb-4">{book.author || 'Unknown Author'}</p>
          
          {book.rating_average && (
            <p className="text-yellow-600 mb-4">★ {book.rating_average} ({book.rating_count} ratings)</p>
          )}

          {book.subjects && (
            <div className="flex flex-wrap gap-2 mb-4">
              {book.subjects_list.map((subject) => (
                <span key={subject} className="px-3 py-1 border border-gray-200 text-gray-600 text-sm">
                  {subject}
                </span>
              ))}
            </div>
          )}

          {book.description && (
            <p className="text-gray-700 mt-4">{book.description}</p>
          )}
        </div>
      </div>

      {book.ai_summary && (
        <div className="border-l-4 border-gray-400 bg-white border border-gray-200 p-5 mb-12">
          <div className="flex items-center gap-2 mb-2">
            <h2 className="font-semibold text-gray-900">AI Summary</h2>
            <span className="text-xs badge px-2 py-0.5">Generated</span>
          </div>
          <p className="text-gray-700">{book.ai_summary}</p>
          {book.ai_sentiment && (
            <p className="text-sm text-gray-500 mt-3 pt-3 border-t">
              Based on reviews: <span className="font-medium capitalize">{book.ai_sentiment}</span> ({book.ai_sentiment_score})
            </p>
          )}
        </div>
      )}

      {(book.has_embeddings || (book.ai_summary || book.ai_sentiment)) && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <h2 className="font-semibold text-gray-900">Search Ready</h2>
            {book.has_embeddings ? (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5">Vectorized</span>
            ) : (
              <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5">Pending</span>
            )}
          </div>
          <p className="text-sm text-gray-500">
            {book.has_embeddings 
              ? 'This book is in the vector database for semantic search.'
              : 'This book is not yet embedded. Add to ChromaDB for search.'}
          </p>
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Similar Books</h2>
        {recLoading ? (
          <p className="text-gray-500">Loading recommendations...</p>
        ) : recommendations && recommendations.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {recommendations.map((rec) => (
              <Link
                key={rec.id}
                to={`/books/${rec.id}`}
                className="bg-white border border-gray-200 overflow-hidden hover:border-gray-300 transition-colors"
              >
                <div className="aspect-[2/3] bg-gray-100">
                  {rec.cover_url ? (
                    <img src={rec.cover_url} alt={rec.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">
                      No Cover
                    </div>
                  )}
                </div>
                <div className="p-3">
                  <p className="font-medium text-gray-900 truncate text-sm">{rec.title}</p>
                  <p className="text-xs text-gray-500 truncate">{rec.author}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No recommendations available</p>
        )}
      </div>

      <button
        onClick={() => setChatOpen(true)}
        className="mt-6 px-6 py-3 bg-gray-900 text-white hover:bg-gray-800"
      >
        Ask about similar books
      </button>

      <ChatModal
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
        bookId={bookId}
        bookTitle={book?.title}
      />
    </div>
  )
}