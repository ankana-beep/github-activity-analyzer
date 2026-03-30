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

// ── Toast ─────────────────────────────────────────────────────────────────────
// Floating notification that auto-dismisses after `duration` ms.
// variant: 'warning' | 'info' | 'success' | 'error'
import { useState, useEffect } from 'react'

const TOAST_STYLES = {
  warning: {
    wrapper: 'bg-amber-50 border-amber-200 text-amber-800',
    icon:    'bg-amber-100 text-amber-600',
    bar:     'bg-amber-400',
    symbol:  '⚠',
  },
  info: {
    wrapper: 'bg-blue-50 border-blue-200 text-blue-800',
    icon:    'bg-blue-100 text-blue-600',
    bar:     'bg-blue-400',
    symbol:  'i',
  },
  success: {
    wrapper: 'bg-green-50 border-green-200 text-green-800',
    icon:    'bg-green-100 text-green-600',
    bar:     'bg-green-400',
    symbol:  '✓',
  },
  error: {
    wrapper: 'bg-red-50 border-red-200 text-red-800',
    icon:    'bg-red-100 text-red-600',
    bar:     'bg-red-400',
    symbol:  '✕',
  },
}

export function Toast({ message, variant = 'warning', duration = 6000, onDismiss }) {
  const [visible, setVisible]   = useState(true)
  const [progress, setProgress] = useState(100)
  const styles = TOAST_STYLES[variant] || TOAST_STYLES.warning

  useEffect(() => {
    if (!message) return

    // Shrink progress bar over `duration` ms
    const step     = 100 / (duration / 50)
    const interval = setInterval(() => {
      setProgress(p => {
        if (p <= 0) { clearInterval(interval); return 0 }
        return p - step
      })
    }, 50)

    // Auto-hide after duration
    const timer = setTimeout(() => {
      setVisible(false)
      onDismiss?.()
    }, duration)

    return () => { clearInterval(interval); clearTimeout(timer) }
  }, [message, duration])

  if (!visible || !message) return null

  return (
    <div
      role="alert"
      className={`
        fixed bottom-6 right-6 z-50 w-80 rounded-2xl border shadow-lg overflow-hidden
        transition-all duration-300
        ${styles.wrapper}
      `}
      style={{ boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}
    >
      {/* Content */}
      <div className="flex items-start gap-3 p-4">
        {/* Icon */}
        <div className={`
          w-7 h-7 rounded-full flex items-center justify-center
          text-xs font-mono font-medium shrink-0 mt-0.5
          ${styles.icon}
        `}>
          {styles.symbol}
        </div>

        {/* Message */}
        <p className="flex-1 text-xs font-mono leading-relaxed">{message}</p>

        {/* Close button */}
        <button
          onClick={() => { setVisible(false); onDismiss?.() }}
          className="shrink-0 opacity-50 hover:opacity-100 transition-opacity text-sm leading-none mt-0.5"
          aria-label="Dismiss"
        >
          ✕
        </button>
      </div>

      {/* Auto-dismiss progress bar */}
      <div className="h-0.5 bg-black/10">
        <div
          className={`h-full transition-none ${styles.bar}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

// ── ToastContainer ────────────────────────────────────────────────────────────
// Renders multiple toasts stacked above each other.
// Pass an array of { id, message, variant } objects.
export function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 items-end">
      {toasts.map((t, i) => (
        <Toast
          key={t.id ?? i}
          message={t.message}
          variant={t.variant || 'warning'}
          duration={t.duration || 6000}
          onDismiss={() => onDismiss?.(t.id ?? i)}
        />
      ))}
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
