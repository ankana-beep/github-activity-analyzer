import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { langColor } from '../../utils/formatters.js'

export default function LanguageChart({ distribution }) {
  if (!distribution || !Object.keys(distribution).length)
    return <p className="text-xs text-zinc-400 font-mono py-8 text-center">No language data</p>

  const data = Object.entries(distribution).map(([name, value]) => ({ name, value, color: langColor(name) }))

  return (
    <div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 mb-3">
        {data.map(d => (
          <span key={d.name} className="flex items-center gap-1.5 text-xs font-mono text-zinc-500">
            <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: d.color }} />
            {d.name} {d.value}%
          </span>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={48} outerRadius={78}
               paddingAngle={2} dataKey="value">
            {data.map(e => <Cell key={e.name} fill={e.color} stroke="none" />)}
          </Pie>
          <Tooltip
            formatter={(v, n) => [`${v}%`, n]}
            contentStyle={{ background:'#fff', border:'1px solid #e4e4e7', borderRadius:'8px', fontSize:'11px', fontFamily:'DM Mono,monospace' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
