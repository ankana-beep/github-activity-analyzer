import { useEffect, useState } from 'react'
import { useReportPoller } from '../hooks/useReportPoller.js'

const STAGES = [
  { key: 'parsing_resume',     label: 'Parsing resume',            detail: 'Extracting text + AI field extraction' },
  { key: 'fetching_github',    label: 'Fetching GitHub activity',  detail: 'Repos, commits, stars, languages' },
  { key: 'analyzing',          label: 'Computing developer score', detail: 'Running weighted activity model' },
  { key: 'generating_insight', label: 'Generating AI insight',     detail: 'Synthesising candidate narrative' },
  { key: 'complete',           label: 'Report ready',              detail: 'All done — loading dashboard' },
]

const ORDER = ['pending','parsing_resume','fetching_github','analyzing','generating_insight','complete']

export default function ProcessingPage({ candidateId, onComplete, onError }) {
  const [status, setStatus] = useState('pending')
  const { startPolling } = useReportPoller()

  useEffect(() => {
    startPolling(
      candidateId,
      data => { setStatus('complete'); setTimeout(() => onComplete(data), 500) },
      onError,
      2500,
    )
  }, [candidateId])

  const cur = ORDER.indexOf(status)

  return (
    <div className="max-w-lg mx-auto pt-8">
      <div className="mb-8">
        <h2 className="font-display text-2xl font-light text-zinc-900 mb-1">Analyzing candidate…</h2>
        <p className="text-xs text-zinc-400 font-mono">Usually takes 15–30 seconds</p>
      </div>

      <div className="space-y-2">
        {STAGES.map((stage, i) => {
          const idx    = i + 1
          const done   = cur > idx
          const active = cur === idx
          const wait   = cur < idx
          return (
            <div key={stage.key}
              className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-300
                ${done   ? 'bg-zinc-900 border-zinc-900 text-white' : ''}
                ${active ? 'bg-white border-zinc-800 shadow-sm' : ''}
                ${wait   ? 'bg-zinc-50 border-zinc-100' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm
                ${done   ? 'bg-white/20 text-white' : ''}
                ${active ? 'bg-zinc-900 text-white' : ''}
                ${wait   ? 'bg-zinc-200 text-zinc-400' : ''}`}
              >
                {done ? '✓' : active ? <SpinIcon /> : String(i + 1)}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-mono font-medium ${done ? 'text-white' : active ? 'text-zinc-900' : 'text-zinc-400'}`}>
                  {stage.label}
                </p>
                <p className={`text-xs font-mono mt-0.5 ${done ? 'text-white/60' : active ? 'text-zinc-500' : 'text-zinc-300'}`}>
                  {stage.detail}
                </p>
              </div>
              <span className={`text-xs font-mono shrink-0 ${done ? 'text-white/70' : active ? 'text-zinc-600' : 'text-zinc-300'}`}>
                {done ? 'done' : active ? 'running' : 'waiting'}
              </span>
            </div>
          )
        })}
      </div>

      <div className="mt-6">
        <div className="w-full h-1 bg-zinc-100 rounded-full overflow-hidden">
          <div className="h-full bg-zinc-900 rounded-full transition-all duration-700"
               style={{ width: `${Math.max(5, cur / STAGES.length * 100)}%` }} />
        </div>
        <p className="text-xs text-zinc-400 font-mono mt-2 text-right">
          {Math.round(Math.max(5, cur / STAGES.length * 100))}% complete
        </p>
      </div>
    </div>
  )
}

const SpinIcon = () => (
  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"/>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
  </svg>
)
