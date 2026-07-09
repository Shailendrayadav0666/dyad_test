import { useState, useEffect } from 'react'
import UploadSection from './components/UploadSection'
import ChatSection from './components/ChatSection'
import { getStatus } from './api/client'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [booting, setBooting] = useState(true)

  useEffect(() => {
    // Prevent browser opening dropped files as a new tab
    const stop = (e) => e.preventDefault()
    document.addEventListener('dragover', stop)
    document.addEventListener('drop', stop)

    // Restore saved session
    const saved = localStorage.getItem('sessionId')
    if (saved) {
      getStatus(saved)
        .then(() => setSessionId(saved))
        .catch(() => localStorage.removeItem('sessionId'))
        .finally(() => setBooting(false))
    } else {
      setBooting(false)
    }

    return () => {
      document.removeEventListener('dragover', stop)
      document.removeEventListener('drop', stop)
    }
  }, [])

  const handleSessionCreated = (id) => {
    localStorage.setItem('sessionId', id)
    setSessionId(id)
  }

  const handleNewSession = () => {
    localStorage.removeItem('sessionId')
    setSessionId(null)
  }

  if (booting) {
    return (
      <div className="boot-screen">
        <span className="spinner lg" />
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">📚</span>
          <div>
            <h1>Exam Prep Chatbot</h1>
            <p>Upload your course materials and ask questions</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        {sessionId ? (
          <ChatSection sessionId={sessionId} onNewSession={handleNewSession} />
        ) : (
          <UploadSection onSessionCreated={handleSessionCreated} />
        )}
      </main>

      <footer className="app-footer">
        Answers grounded in your uploaded course materials
      </footer>
    </div>
  )
}
