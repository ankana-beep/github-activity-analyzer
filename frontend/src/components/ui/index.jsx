// ── Badge ─────────────────────────────────────────────────────────────────────
export function Badge({ children, className = '' }) {
  return (
    <span className={`text-xs font-mono px-2.5 py-1 rounded-full border ${className}`}>
      {children}
    </span>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────
export function Card({ children, className = '' }) {
  return (
    <div className={`bg-white border border-zinc-200 rounded-2xl p-5 ${className}`}>
      {children}
    </div>
  )
}

// ── SectionTitle ──────────────────────────────────────────────────────────────
export function SectionTitle({ children }) {
  return (
    <p className="text-[10px] font-mono uppercase tracking-widest text-zinc-400 mb-3">
      {children}
    </p>
  )
}

// ── MetricCard ────────────────────────────────────────────────────────────────
export function MetricCard({ label, value, sub }) {
  return (
    <div className="bg-zinc-50 rounded-xl p-3 border border-zinc-100">
      <p className="text-[10px] text-zinc-400 font-mono uppercase tracking-wide mb-1">{label}</p>
      <p className="text-lg font-display font-light text-zinc-900 leading-none">{value}</p>
      {sub && <p className="text-[10px] text-zinc-400 font-mono mt-1">{sub}</p>}
    </div>
  )
}

// ── ErrorBanner ───────────────────────────────────────────────────────────────
export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-sm font-mono text-red-700 mb-4">
      <span className="shrink-0 mt-0.5">✕</span>
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 text-red-400 hover:text-red-600">✕</button>
      )}
    </div>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 'sm' }) {
  const cls = size === 'lg' ? 'w-8 h-8 border-[3px]' : 'w-4 h-4 border-2'
  return (
    <span className={`${cls} border-zinc-200 border-t-zinc-800 rounded-full animate-spin inline-block`} />
  )
}

// ── ScoreRing ─────────────────────────────────────────────────────────────────
export function ScoreRing({ score, grade, gradeClass, size = 'md' }) {
  const pct = Math.min(score ?? 0, 100)
  const r = size === 'sm' ? 30 : 44
  const circ = 2 * Math.PI * r
  const offset = circ - (pct / 100) * circ
  const dim = size === 'sm' ? 'w-20 h-20' : 'w-28 h-28'
  const numSize = size === 'sm' ? 'text-lg' : 'text-2xl'

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`relative ${dim}`}>
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={r} fill="none" stroke="#f4f4f5" strokeWidth="8" />
          <circle cx="50" cy="50" r={r} fill="none" stroke="#18181b" strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-display font-light leading-none text-zinc-900 ${numSize}`}>{score ?? '–'}</span>
          <span className="text-[9px] text-zinc-400 font-mono mt-0.5">/ 100</span>
        </div>
      </div>
      {grade && (
        <span className={`text-xs font-mono px-3 py-0.5 rounded-full border ${gradeClass}`}>{grade}</span>
      )}
    </div>
  )
}

// ── ProgressBar ───────────────────────────────────────────────────────────────
export function ProgressBar({ value, color = 'bg-zinc-800', label }) {
  return (
    <div>
      {label && (
        <div className="flex justify-between text-[10px] font-mono text-zinc-400 mb-1">
          <span>{label}</span>
          <span>{Math.round(value)}%</span>
        </div>
      )}
      <div className="h-1.5 bg-zinc-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}
