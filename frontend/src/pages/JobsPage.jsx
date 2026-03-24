import { useState, useEffect } from 'react'
import { listJobs, createJob, deleteJob, computeCompatibility } from '../services/api.js'
import { Card, SectionTitle, ScoreRing, ProgressBar, ErrorBanner, Badge, Spinner } from '../components/ui/index.jsx'
import CompatibilityRadar from '../components/charts/CompatibilityRadar.jsx'
import { matchColors, gradeColors } from '../utils/formatters.js'
import { getDownloadUrl } from '../services/api.js'

export default function JobsPage({ candidateId, reportData }) {
  const [jobs,        setJobs]        = useState([])
  const [results,     setResults]     = useState({})  // jobId → CompatibilitySchema
  const [loading,     setLoading]     = useState({})  // jobId → bool
  const [error,       setError]       = useState(null)
  const [showForm,    setShowForm]    = useState(false)
  const [form,        setForm]        = useState(defaultForm())
  const [creating,    setCreating]    = useState(false)
  const [selected,    setSelected]    = useState(null)  // jobId for detail view

  useEffect(() => { fetchJobs() }, [])

  const fetchJobs = async () => {
    try { setJobs(await listJobs()) } catch { setError('Failed to load jobs.') }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!form.title.trim() || !form.description.trim()) return
    setCreating(true)
    try {
      const payload = {
        ...form,
        required_skills: form.required_skills.split(',').map(s => s.trim()).filter(Boolean),
        preferred_skills: form.preferred_skills.split(',').map(s => s.trim()).filter(Boolean),
        experience_years: form.experience_years ? parseFloat(form.experience_years) : null,
      }
      const job = await createJob(payload)
      setJobs(prev => [job, ...prev])
      setShowForm(false); setForm(defaultForm())
    } catch { setError('Failed to create job.') }
    finally { setCreating(false) }
  }

  const handleDelete = async (jobId) => {
    await deleteJob(jobId)
    setJobs(prev => prev.filter(j => j.id !== jobId))
    if (selected === jobId) setSelected(null)
  }

  const handleMatch = async (jobId) => {
    if (!candidateId) { setError('No candidate loaded. Upload a resume first.'); return }
    if (!reportData || reportData.status !== 'complete') { setError('Candidate analysis not complete.'); return }
    setLoading(prev => ({ ...prev, [jobId]: true }))
    setError(null)
    try {
      const result = await computeCompatibility(candidateId, jobId)
      setResults(prev => ({ ...prev, [jobId]: result }))
      setSelected(jobId)
    } catch (e) {
      setError(e.response?.data?.detail || 'Compatibility scoring failed.')
    } finally {
      setLoading(prev => ({ ...prev, [jobId]: false }))
    }
  }

  const selectedResult = selected && results[selected]
  const selectedJob    = selected && jobs.find(j => j.id === selected)

  return (
    <div>
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-zinc-100">
        <h2 className="font-display text-xl font-light text-zinc-900">Job Compatibility</h2>
        <button onClick={() => setShowForm(s => !s)}
          className="text-xs font-mono px-3 py-1.5 border border-zinc-200 rounded-lg
            hover:border-zinc-400 text-zinc-600 hover:text-zinc-900 transition-colors">
          {showForm ? '✕ Cancel' : '+ Add Job'}
        </button>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Job creation form */}
      {showForm && (
        <Card className="mb-6">
          <SectionTitle>New job posting</SectionTitle>
          <form onSubmit={handleCreate} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Input label="Job title *" value={form.title} onChange={v => setForm(f => ({...f, title: v}))} />
              <Input label="Company" value={form.company} onChange={v => setForm(f => ({...f, company: v}))} />
            </div>
            <Textarea label="Job description *" value={form.description} onChange={v => setForm(f => ({...f, description: v}))} rows={4} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Required skills (comma-separated)" value={form.required_skills} onChange={v => setForm(f => ({...f, required_skills: v}))} />
              <Input label="Preferred skills (comma-separated)" value={form.preferred_skills} onChange={v => setForm(f => ({...f, preferred_skills: v}))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input label="Years of experience" type="number" value={form.experience_years} onChange={v => setForm(f => ({...f, experience_years: v}))} />
              <Input label="Location" value={form.location} onChange={v => setForm(f => ({...f, location: v}))} />
            </div>
            <button type="submit" disabled={creating}
              className="w-full py-2.5 bg-zinc-900 text-white text-sm font-mono rounded-xl
                hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              {creating ? 'Creating…' : 'Create Job Posting'}
            </button>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Job list */}
        <div className="space-y-3">
          {!jobs.length && (
            <p className="text-sm font-mono text-zinc-400 py-8 text-center">
              No jobs yet. Add one to start matching.
            </p>
          )}
          {jobs.map(job => {
            const res = results[job.id]
            const matchClass = res ? (matchColors[res.match_level] || matchColors.Poor) : ''
            return (
              <div key={job.id}
                onClick={() => res && setSelected(job.id)}
                className={`bg-white border rounded-2xl p-4 cursor-pointer transition-all
                  ${selected === job.id ? 'border-zinc-800 shadow-sm' : 'border-zinc-200 hover:border-zinc-300'}
                  ${res ? 'cursor-pointer' : ''}`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="min-w-0">
                    <p className="text-sm font-mono font-medium text-zinc-900 truncate">{job.title}</p>
                    {job.company && <p className="text-xs font-mono text-zinc-400">{job.company}</p>}
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {res && (
                      <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${matchClass}`}>
                        {res.score}% · {res.match_level}
                      </span>
                    )}
                    <button onClick={e => { e.stopPropagation(); handleDelete(job.id) }}
                      className="text-zinc-300 hover:text-red-400 text-xs px-1">✕</button>
                  </div>
                </div>
                <p className="text-xs font-mono text-zinc-400 line-clamp-2 mb-3">{job.description}</p>
                {job.required_skills?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {job.required_skills.slice(0,5).map(s => (
                      <span key={s} className="text-[10px] font-mono px-2 py-0.5 bg-zinc-100 text-zinc-600 rounded-md">{s}</span>
                    ))}
                  </div>
                )}
                <button
                  onClick={e => { e.stopPropagation(); handleMatch(job.id) }}
                  disabled={loading[job.id] || !candidateId}
                  className="w-full py-2 text-xs font-mono border border-zinc-200 rounded-lg
                    hover:bg-zinc-50 hover:border-zinc-400 disabled:opacity-30 disabled:cursor-not-allowed
                    transition-colors flex items-center justify-center gap-2"
                >
                  {loading[job.id] ? <><Spinner /><span>Computing…</span></> : 'Compute Match →'}
                </button>
              </div>
            )
          })}
        </div>

        {/* Compatibility detail panel */}
        <div>
          {selectedResult && selectedJob ? (
            <CompatibilityDetail result={selectedResult} job={selectedJob} candidateId={candidateId} />
          ) : (
            <div className="bg-zinc-50 border border-zinc-100 rounded-2xl h-48 flex items-center justify-center">
              <p className="text-xs font-mono text-zinc-400 text-center px-4">
                {!candidateId
                  ? 'Upload a resume first to enable compatibility scoring.'
                  : 'Select a job and click "Compute Match" to see the compatibility report.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function CompatibilityDetail({ result, job, candidateId }) {
  const matchClass = matchColors[result.match_level] || matchColors.Poor
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="font-mono font-medium text-sm text-zinc-900">{job.title}</p>
          {job.company && <p className="text-xs font-mono text-zinc-400">{job.company}</p>}
        </div>
        <div className="text-right">
          <p className="font-display text-2xl font-light text-zinc-900">{result.score}</p>
          <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${matchClass}`}>
            {result.match_level}
          </span>
        </div>
      </div>

      <CompatibilityRadar compatibility={result} />

      <div className="space-y-2.5 mt-4">
        <ProgressBar value={result.skill_match}       label="Skill match"      color="bg-violet-500" />
        <ProgressBar value={result.experience_match}  label="Experience match" color="bg-blue-500" />
        <ProgressBar value={result.github_relevance}  label="GitHub relevance" color="bg-teal-500" />
        <ProgressBar value={result.language_match}    label="Language match"   color="bg-amber-500" />
      </div>

      {result.matched_skills?.length > 0 && (
        <div className="mt-4">
          <SectionTitle>Matched skills</SectionTitle>
          <div className="flex flex-wrap gap-1">
            {result.matched_skills.map(s => (
              <span key={s} className="text-[10px] font-mono px-2 py-0.5 bg-green-50 text-green-700 border border-green-200 rounded-md">{s}</span>
            ))}
          </div>
        </div>
      )}

      {result.missing_skills?.length > 0 && (
        <div className="mt-3">
          <SectionTitle>Missing skills</SectionTitle>
          <div className="flex flex-wrap gap-1">
            {result.missing_skills.map(s => (
              <span key={s} className="text-[10px] font-mono px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 rounded-md">{s}</span>
            ))}
          </div>
        </div>
      )}

      {result.explanation && (
        <div className="mt-4 pt-4 border-t border-zinc-100">
          <SectionTitle>AI assessment</SectionTitle>
          <p className="font-display text-sm font-light text-zinc-700 italic leading-relaxed">
            {result.explanation}
          </p>
        </div>
      )}

      <a href={getDownloadUrl(candidateId, job.id)} target="_blank" rel="noreferrer"
        className="mt-4 flex items-center justify-center w-full py-2 text-xs font-mono border
          border-zinc-200 rounded-lg hover:bg-zinc-50 hover:border-zinc-400 transition-colors text-zinc-600">
        ↓ Download PDF with compatibility
      </a>
    </Card>
  )
}

// ── Small form helpers ────────────────────────────────────────────────────────

const Input = ({ label, value, onChange, type = 'text' }) => (
  <div>
    <p className="text-[10px] font-mono text-zinc-400 mb-1">{label}</p>
    <input type={type} value={value} onChange={e => onChange(e.target.value)}
      className="w-full text-xs font-mono px-3 py-2 border border-zinc-200 rounded-lg
        bg-white text-zinc-900 focus:outline-none focus:border-zinc-400 transition-colors" />
  </div>
)

const Textarea = ({ label, value, onChange, rows = 3 }) => (
  <div>
    <p className="text-[10px] font-mono text-zinc-400 mb-1">{label}</p>
    <textarea value={value} onChange={e => onChange(e.target.value)} rows={rows}
      className="w-full text-xs font-mono px-3 py-2 border border-zinc-200 rounded-lg
        bg-white text-zinc-900 focus:outline-none focus:border-zinc-400 transition-colors resize-none" />
  </div>
)

function defaultForm() {
  return { title: '', company: '', description: '', required_skills: '', preferred_skills: '', experience_years: '', location: '' }
}
