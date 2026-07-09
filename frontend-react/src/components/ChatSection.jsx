import { useState, useEffect, useRef } from 'react'
import Message from './Message'
import { getAnswer } from '../api/client'

export default function ChatSection({ sessionId, onNewSession }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem(`history_${sessionId}`) || '[]')
    setMessages(saved)
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const submit = async () => {
    const q = input.trim()
    if (!q || sending) return

    setInput('')
    setError('')
    setSending(true)

    const userMsg = { role: 'user', text: q }
    setMessages((prev) => [...prev, userMsg])

    try {
      const data = await getAnswer(sessionId, q)
      const assistantMsg = {
        role: 'assistant',
        text: data.answer,
        citations: data.citations || [],
      }
      setMessages((prev) => {
        const next = [...prev, assistantMsg]
        localStorage.setItem(`history_${sessionId}`, JSON.stringify(next))
        return next
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
      textareaRef.current?.focus()
    }
  }

  return (
    <div className="chat-shell">
      <div className="chat-header">
        <h2>Chat with your document</h2>
        <button className="btn btn-secondary" onClick={onNewSession}>
          <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fillRule="evenodd"
              d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z"
              clipRule="evenodd" />
          </svg>
          New PDF
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !sending && (
          <div className="chat-empty">
            Ask a question about your document to get started
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}

        {sending && (
          <div className="message assistant">
            <div className="bubble">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && <div className="status-bar error">{error}</div>}

      <div className="chat-input-row">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) submit() }}
          placeholder="Ask a question… (Ctrl+Enter to send)"
          rows={3}
          disabled={sending}
        />
        <button
          className="btn btn-primary send-btn"
          onClick={submit}
          disabled={sending || !input.trim()}
        >
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
          Send
        </button>
      </div>
    </div>
  )
}
