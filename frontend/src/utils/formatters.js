export const fmt = (n) => {
  if (n == null) return '–'
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'k'
  return String(n)
}

export const timeAgo = (iso) => {
  if (!iso) return '–'
  const d = Math.floor((Date.now() - new Date(iso)) / 86_400_000)
  if (d === 0) return 'today'
  if (d === 1) return 'yesterday'
  if (d < 30)  return `${d}d ago`
  if (d < 365) return `${Math.floor(d / 30)}mo ago`
  return `${Math.floor(d / 365)}y ago`
}

export const truncate = (s, n = 60) =>
  s && s.length > n ? s.slice(0, n) + '…' : (s || '')

export const LANG_COLORS = {
  JavaScript:'#f1e05a', TypeScript:'#3178c6', Python:'#3572A5',
  Rust:'#dea584', Go:'#00ADD8', Java:'#b07219', 'C++':'#f34b7d',
  C:'#555555', Ruby:'#701516', Swift:'#F05138', Kotlin:'#A97BFF',
  PHP:'#4F5D95', Shell:'#89e051', HTML:'#e34c26', CSS:'#563d7c',
  Dart:'#00B4AB', Scala:'#c22d40', R:'#198CE7', Elixir:'#6e4a7e',
}
export const langColor = (l) => LANG_COLORS[l] || '#8b8b8b'

export const gradeColors = {
  Elite:     'text-violet-700 bg-violet-50 border-violet-200',
  Senior:    'text-blue-700 bg-blue-50 border-blue-200',
  'Mid-level':'text-teal-700 bg-teal-50 border-teal-200',
  Junior:    'text-amber-700 bg-amber-50 border-amber-200',
  Entry:     'text-zinc-500 bg-zinc-100 border-zinc-200',
}

export const matchColors = {
  Excellent: 'text-green-700 bg-green-50 border-green-200',
  Good:      'text-blue-700 bg-blue-50 border-blue-200',
  Moderate:  'text-amber-700 bg-amber-50 border-amber-200',
  Poor:      'text-red-700 bg-red-50 border-red-200',
}
