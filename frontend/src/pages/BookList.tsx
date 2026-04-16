import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchBooks } from '../services/api'
import { BookListItem } from '../types'

const genres = [
  'Fantasy', 'Romance', 'Mystery', 'Science Fiction', 'History',
  'True Crime', 'Technology', 'Sports', 'Self Help', 'Religion',
  'Psychology', 'Politics', 'Health', 'Business', 'Biographies'
]

function SkeletonCard() {
  return (
    <div className="bg-white border border-gray-200 overflow-hidden">
      <div className="aspect-[2/3] skeleton" />
      <div className="p-4 space-y-3">
        <div className="h-4 skeleton w-3/4" />
        <div className="h-3 skeleton w-1/2" />
      </div>
    </div>
  )
}

export default function BookList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [genre, setGenre] = useState(searchParams.get('genre') || '')
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['books', search, genre, page],
    queryFn: () => fetchBooks({ search, genre, page }),
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (genre) params.set('genre', genre)
    params.set('page', '1')
    setSearchParams(params)
    setPage(1)
  }

  const handleGenreChange = (newGenre: string) => {
    setGenre(newGenre)
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (newGenre) params.set('genre', newGenre)
    params.set('page', '1')
    setSearchParams(params)
    setPage(1)
  }

  return (
    <div>
      <form onSubmit={handleSearch} className="mb-8 flex gap-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search books..."
          className="flex-1 px-3 py-2 border border-gray-300 focus:border-gray-400 focus:ring-0"
        />
        <select
          value={genre}
          onChange={(e) => handleGenreChange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded focus:border-gray-400 focus:ring-0"
        >
          <option value="">All Genres</option>
          {genres.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
        <button
          type="submit"
          className="px-6 py-2 bg-gray-900 text-white hover:bg-gray-800"
        >
          Search
        </button>
      </form>

      {isError && (
        <p className="text-red-600">Failed to load books. Make sure the backend is running.</p>
      )}

      {!isLoading && data && data.results.length === 0 && (
        <p className="text-gray-500 text-center py-8">No books found</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {isLoading ? (
          Array.from({ length: 20 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          data?.results.map((book: BookListItem) => (
            <Link
              key={book.id}
              to={`/books/${book.id}`}
              className="bg-white border border-gray-200 overflow-hidden hover:border-gray-300 transition-colors"
            >
              <div className="aspect-[2/3] bg-gray-100 relative overflow-hidden">
                {book.cover_url ? (
                  <img
                    src={book.cover_url}
                    alt={book.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    No Cover
                  </div>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-medium text-gray-900 truncate">{book.title}</h3>
                <p className="text-sm text-gray-500 truncate">{book.author || 'Unknown'}</p>
                {book.rating_average && (
                  <p className="text-sm text-yellow-600">★ {book.rating_average}</p>
                )}
              </div>
            </Link>
          ))
        )}
      </div>

      {data && data.count > page * 20 && (
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={() => {
              setPage(page - 1)
              setSearchParams((prev) => {
                prev.set('page', String(page - 1))
                return prev
              })
            }}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 bg-white disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => {
              setPage(page + 1)
              setSearchParams((prev) => {
                prev.set('page', String(page + 1))
                return prev
              })
            }}
            className="px-4 py-2 border border-gray-300 bg-white"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}