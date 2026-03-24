import { useState, useRef } from 'react'
import { uploadResume } from '../../services/api.js'
import { ErrorBanner } from '../ui/index.jsx'

const ALLOWED_EXT  = ['.pdf', '.docx']

export default function ResumeUploader({ onSuccess }) {
  const [dragging,   setDragging]  = useState(false)
  const [file,       setFile]      = useState(null)
  const [uploading,  setUploading] = useState(false)
  const [progress,   setProgress]  = useState(0)
  const [error,      setError]     = useState(null)
  const ref = useRef(null)

  const handleFile = (f) => {
    const ext = '.' + (f.name.split('.').pop() || '').toLowerCase()
    if (!ALLOWED_EXT.includes(ext)) { setError('Only PDF and DOCX accepted.'); return }
    if (f.size > 10 * 1024 * 1024) { setError('File exceeds 10 MB.'); return }
    setError(null); setFile(f)
  }

  const submit = async () => {
    if (!file) return
    setUploading(true); setProgress(0); setError(null)
    try {
      const res = await uploadResume(file, e => e.total && setProgress(Math.round(e.loaded / e.total * 100)))
      onSuccess(res.candidate_id)
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed.')
      setUploading(false)
    }
  }

  return (
    <div className="w-full">
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      <div
        onClick={() => !uploading && ref.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
          ${dragging ? 'border-zinc-800 bg-zinc-100' : 'border-zinc-300 bg-white hover:border-zinc-400 hover:bg-zinc-50'}
          ${file ? 'border-zinc-500' : ''}`}
      >
        <input ref={ref} type="file" accept=".pdf,.docx" className="hidden"
               onChange={e => e.target.files[0] && handleFile(e.target.files[0])} disabled={uploading} />
        {file ? (
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white rounded-lg text-sm font-mono">
              <DocIcon /> <span className="max-w-xs truncate">{file.name}</span>
            </div>
            <p className="text-xs text-zinc-400 font-mono">{(file.size / 1024).toFixed(0)} KB · click to change</p>
          </div>
        ) : (
          <div className="space-y-3">
            <UploadIcon />
            <p className="text-sm font-mono font-medium text-zinc-700">Drop resume here or click to browse</p>
            <p className="text-xs text-zinc-400 font-mono">PDF or DOCX · max 10 MB</p>
          </div>
        )}
      </div>

      {uploading && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-zinc-400 font-mono mb-1">
            <span>Uploading…</span><span>{progress}%</span>
          </div>
          <div className="w-full h-1 bg-zinc-100 rounded-full overflow-hidden">
            <div className="h-full bg-zinc-900 rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      <button onClick={submit} disabled={!file || uploading}
        className="mt-4 w-full py-3 bg-zinc-900 text-white text-sm font-mono rounded-xl
          hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
        {uploading ? 'Uploading…' : 'Analyze Candidate →'}
      </button>
    </div>
  )
}

const UploadIcon = () => (
  <svg className="mx-auto w-10 h-10 text-zinc-300" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
  </svg>
)
const DocIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
  </svg>
)
