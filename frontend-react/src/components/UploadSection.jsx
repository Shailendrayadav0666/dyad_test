import { useState, useRef, useCallback } from 'react'
import { uploadPdf } from '../api/client'

const STAGES = [
  'Uploading PDF…',
  'Extracting text…',
  'Generating embeddings…',
  'Indexing into vector store…',
]

export default function UploadSection({ onSessionCreated }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [status, setStatus] = useState({ type: '', text: '' })
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef(null)
  const timerRef = useRef(null)

  const validateAndSet = useCallback((f) => {
    if (!f) return
    if (f.type !== 'application/pdf') {
      setStatus({ type: 'error', text: 'Only PDF files are supported' })
      return
    }
    if (f.size > 50 * 1024 * 1024) {
      setStatus({ type: 'error', text: 'File must be less than 50 MB' })
      return
    }
    setFile(f)
    setStatus({ type: '', text: '' })
  }, [])

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      e.stopPropagation()
      setDragging(false)
      validateAndSet(e.dataTransfer.files[0])
    },
    [validateAndSet]
  )

  const handleUpload = async () => {
    if (!file || uploading) return
    setUploading(true)
    let stage = 0
    setStatus({ type: 'loading', text: STAGES[0] })

    timerRef.current = setInterval(() => {
      stage = Math.min(stage + 1, STAGES.length - 1)
      setStatus({ type: 'loading', text: STAGES[stage] })
    }, 1800)

    try {
      const data = await uploadPdf(file)
      clearInterval(timerRef.current)
      setStatus({ type: 'success', text: `Ready — ${data.pdf_info.pages} pages indexed` })
      setTimeout(() => onSessionCreated(data.session_id), 500)
    } catch (err) {
      clearInterval(timerRef.current)
      setStatus({ type: 'error', text: err.message })
      setUploading(false)
    }
  }

  const sizeMB = file ? (file.size / (1024 * 1024)).toFixed(2) : null

  return (
    <div className="upload-card">
      <div
        className={`upload-zone${dragging ? ' dragging' : ''}${file ? ' selected' : ''}`}
        onClick={() => !uploading && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); setDragging(true) }}
        onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget)) setDragging(false) }}
        onDrop={handleDrop}
      >
        <div className="upload-zone-icon">
          {file ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
            </svg>
          )}
        </div>

        {file ? (
          <div className="upload-file-info">
            <strong>{file.name}</strong>
            <span>{sizeMB} MB · PDF</span>
          </div>
        ) : (
          <div className="upload-hint">
            <span>Drag &amp; drop your PDF here</span>
            <small>or click to browse &middot; max 50 MB</small>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          style={{ display: 'none' }}
          onChange={(e) => { setFile(null); validateAndSet(e.target.files[0]) }}
        />
      </div>

      {status.text && (
        <div className={`status-bar ${status.type}`}>
          {status.type === 'loading' && <span className="spinner" />}
          {status.text}
        </div>
      )}

      {file && !uploading && (
        <button className="btn btn-primary upload-btn" onClick={handleUpload}>
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fillRule="evenodd"
              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
              clipRule="evenodd" />
          </svg>
          Upload &amp; Process
        </button>
      )}
    </div>
  )
}
