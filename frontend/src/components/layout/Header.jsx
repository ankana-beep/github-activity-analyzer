export default function Header({ onLogoClick }) {
  return (
    <header className="border-b border-zinc-200 bg-white sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <button onClick={onLogoClick} className="flex items-center gap-2.5 hover:opacity-75 transition-opacity">
          <div className="w-7 h-7 bg-zinc-900 rounded flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-display font-light">R</span>
          </div>
          <span className="font-display text-base font-light tracking-tight text-zinc-900">
            Recruiter Intelligence
          </span>
        </button>
        <span className="text-xs text-zinc-400 font-mono">v2.0</span>
      </div>
    </header>
  )
}
