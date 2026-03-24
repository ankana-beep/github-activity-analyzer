import ResumeUploader from '../components/ui/ResumeUploader.jsx'

const FEATURES = [
  { icon: '📄', label: 'AI Resume Parsing',     desc: 'Name, email, skills, experience, education' },
  { icon: '🐙', label: 'GitHub Analysis',        desc: 'Repos, stars, commits, language distribution' },
  { icon: '📊', label: 'Developer Score',        desc: 'Weighted metric from activity & impact' },
  { icon: '🤝', label: 'Job Compatibility',      desc: 'Match skills + GitHub to any job description' },
  { icon: '🤖', label: 'AI Insight',             desc: 'Plain-language recruiter summary from Claude' },
  { icon: '📥', label: 'PDF Report Download',    desc: 'Professional report with all insights' },
]

export default function UploadPage({ onSuccess }) {
  return (
    <div className="max-w-xl mx-auto pt-4">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-light tracking-tight text-zinc-900 mb-2">
          Analyze a candidate
        </h1>
        <p className="text-sm text-zinc-500 font-mono leading-relaxed">
          Upload a resume. The platform parses it with AI, fetches GitHub activity,
          scores the developer, matches job descriptions, and exports a PDF report.
        </p>
      </div>

      <ResumeUploader onSuccess={onSuccess} />

      <div className="mt-10 grid grid-cols-2 gap-3">
        {FEATURES.map(({ icon, label, desc }) => (
          <div key={label} className="p-4 bg-white border border-zinc-100 rounded-xl">
            <span className="text-xl">{icon}</span>
            <p className="text-xs font-mono font-medium text-zinc-700 mt-2">{label}</p>
            <p className="text-xs font-mono text-zinc-400 mt-0.5 leading-snug">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
