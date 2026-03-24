import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'

export default function CompatibilityRadar({ compatibility }) {
  if (!compatibility) return null

  const data = [
    { subject: 'Skills',      value: Math.round(compatibility.skill_match) },
    { subject: 'Experience',  value: Math.round(compatibility.experience_match) },
    { subject: 'GitHub',      value: Math.round(compatibility.github_relevance) },
    { subject: 'Languages',   value: Math.round(compatibility.language_match) },
    { subject: 'Overall',     value: Math.round(compatibility.score) },
  ]

  return (
    <ResponsiveContainer width="100%" height={220}>
      <RadarChart data={data}>
        <PolarGrid stroke="#e4e4e7" />
        <PolarAngleAxis
          dataKey="subject"
          tick={{ fontSize: 10, fontFamily: 'DM Mono,monospace', fill: '#71717a' }}
        />
        <Radar
          dataKey="value"
          stroke="#18181b"
          fill="#18181b"
          fillOpacity={0.12}
          strokeWidth={1.5}
        />
        <Tooltip
          contentStyle={{ background:'#fff', border:'1px solid #e4e4e7', borderRadius:'8px', fontSize:'11px', fontFamily:'DM Mono,monospace' }}
          formatter={v => [`${v}%`]}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
