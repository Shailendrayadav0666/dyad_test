import { useState } from 'react'

function timestamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function Message({ message }) {
  const [showCitations, setShowCitations] = useState(false)
  const isUser = message.role === 'user'
  const hasCitations = message.citations?.length > 0

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="bubble">
        <p className="message-text">{message.text}</p>

        {hasCitations && (
          <div className="citations">
            <button
              className="citations-toggle"
              onClick={() => setShowCitations((s) => !s)}
            >
              <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
                <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
              </svg>
              {showCitations ? 'Hide' : 'Show'} sources ({message.citations.length})
            </button>

            {showCitations && (
              <div className="citations-list">
                {message.citations.map((c, i) => (
                  <div key={i} className="citation-card">
                    <div className="citation-meta">
                      <span className="citation-rank">#{i + 1}</span>
                      <span className="citation-score">
                        {(c.similarity_score * 100).toFixed(0)}% match
                      </span>
                    </div>
                    <p className="citation-text">
                      {c.chunk_text.length > 220
                        ? c.chunk_text.slice(0, 220) + '…'
                        : c.chunk_text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      <span className="message-time">{timestamp()}</span>
    </div>
  )
}
