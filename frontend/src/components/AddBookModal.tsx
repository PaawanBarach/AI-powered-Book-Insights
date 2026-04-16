import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'

interface AddBookModalProps {
  isOpen: boolean
  onClose: () => void
}

interface BookForm {
  title: string
  author: string
  description: string
  subjects: string
  cover_url: string
}

export function AddBookModal({ isOpen, onClose }: AddBookModalProps) {
  const [form, setForm] = useState<BookForm>({
    title: '',
    author: '',
    description: '',
    subjects: '',
    cover_url: '',
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/books/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error('Failed to create book')
      return res.json()
    },
    onSuccess: () => {
      setForm({ title: '', author: '', description: '', subjects: '', cover_url: '' })
      onClose()
      window.location.reload()
    },
  })

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title.trim()) return
    createMutation.mutate()
  }

  const updateField = (field: keyof BookForm) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white w-full max-w-md p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-semibold">Add Book</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            value={form.title}
            onChange={updateField('title')}
            placeholder="Title *"
            className="w-full px-3 py-2 border border-gray-300 text-sm focus:border-gray-400 focus:ring-0"
          />
          <input
            type="text"
            value={form.author}
            onChange={updateField('author')}
            placeholder="Author"
            className="w-full px-3 py-2 border border-gray-300 text-sm focus:border-gray-400 focus:ring-0"
          />
          <textarea
            value={form.description}
            onChange={updateField('description')}
            placeholder="Description"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 text-sm focus:border-gray-400 focus:ring-0"
          />
          <input
            type="text"
            value={form.subjects}
            onChange={updateField('subjects')}
            placeholder="Subjects (comma separated)"
            className="w-full px-3 py-2 border border-gray-300 text-sm focus:border-gray-400 focus:ring-0"
          />
          <input
            type="text"
            value={form.cover_url}
            onChange={updateField('cover_url')}
            placeholder="Cover URL"
            className="w-full px-3 py-2 border border-gray-300 text-sm focus:border-gray-400 focus:ring-0"
          />

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || !form.title.trim()}
              className="flex-1 px-4 py-2 bg-gray-900 text-white text-sm hover:bg-gray-800 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Adding...' : 'Add Book'}
            </button>
          </div>
          {createMutation.isError && (
            <p className="text-red-600 text-sm">Failed to add book</p>
          )}
        </form>
      </div>
    </div>
  )
}