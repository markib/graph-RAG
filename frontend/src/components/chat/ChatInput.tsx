import { useState, type FormEvent } from 'react'

type Props = {
  onSubmit: (value: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSubmit, disabled }: Props) {
  const [value, setValue] = useState('')

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) return
    onSubmit(trimmed)
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="flex-1 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
        placeholder="Ask the graph a question..."
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="inline-flex items-center rounded-2xl bg-sky-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        Send
      </button>
    </form>
  )
}
