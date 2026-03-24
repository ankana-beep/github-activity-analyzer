import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

export default function ActivityTimeline({ commitActivity }) {
  if (!commitActivity?.length)
    return <p className="text-xs text-zinc-400 font-mono py-8 text-center">No commit data</p>

  const data = commitActivity.map((commits, i) => ({ month: MONTHS[i % 12], commits }))
  const max  = Math.max(...data.map(d => d.commits), 1)

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} barCategoryGap="25%">
        <XAxis dataKey="month" tick={{ fontSize: 10, fontFamily: 'DM Mono,monospace', fill: '#a1a1aa' }}
               axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fontFamily: 'DM Mono,monospace', fill: '#a1a1aa' }}
               axisLine={false} tickLine={false} width={24} />
        <Tooltip cursor={{ fill: '#f4f4f5' }}
          contentStyle={{ background:'#fff', border:'1px solid #e4e4e7', borderRadius:'8px', fontSize:'11px', fontFamily:'DM Mono,monospace' }}
          formatter={v => [v, 'commits']} />
        <Bar dataKey="commits" radius={[3,3,0,0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.commits === max ? '#18181b' : d.commits > max * 0.6 ? '#52525b' : '#d4d4d8'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
