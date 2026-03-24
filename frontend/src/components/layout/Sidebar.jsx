const NAV = [
  { key: 'dashboard', label: 'Dashboard', icon: '▦' },
  { key: 'jobs',      label: 'Job Compatibility', icon: '◈' },
]

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="w-48 shrink-0 border-r border-zinc-200 bg-white px-3 py-6 hidden sm:block">
      <p className="text-[10px] font-mono uppercase tracking-widest text-zinc-400 mb-3 px-2">
        Navigation
      </p>
      <nav className="space-y-1">
        {NAV.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => onNavigate(key)}
            className={`w-full text-left flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-mono
              transition-colors
              ${activePage === key
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'
              }`}
          >
            <span className="text-base leading-none">{icon}</span>
            {label}
          </button>
        ))}
      </nav>
    </aside>
  )
}
