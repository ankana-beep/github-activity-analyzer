import { Card, SectionTitle, MetricCard, ScoreRing, ProgressBar, ErrorBanner } from '../components/ui/index.jsx'
import LanguageChart from '../components/charts/LanguageChart.jsx'
import ActivityTimeline from '../components/charts/ActivityTimeline.jsx'
import { fmt, timeAgo, truncate, gradeColors, matchColors } from '../utils/formatters.js'
import { getDownloadUrl } from '../services/api.js'

export default function DashboardPage({ data, onReset, onNavigate }) {
  if (!data) return null
  const { parsed_resume: r, github_activity: gh, developer_score, score_grade, ai_insight } = data
  const profile   = gh?.profile
  const initials  = (profile?.name || r?.name || '?').split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase()
  const gradeClass = gradeColors[score_grade] || gradeColors.Entry

  return (
    <div>
      {/* Nav bar */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-zinc-100">
        <h2 className="font-display text-xl font-light text-zinc-900">Developer Insights Report</h2>
        <div className="flex gap-2">
          <a href={getDownloadUrl(data.candidate_id)} target="_blank" rel="noreferrer"
            className="text-xs font-mono text-zinc-600 border border-zinc-200 hover:border-zinc-400
              px-3 py-1.5 rounded-lg transition-colors hover:text-zinc-900">
            ↓ Download PDF
          </a>
          <button onClick={onReset}
            className="text-xs font-mono text-zinc-500 border border-zinc-200 hover:border-zinc-400
              px-3 py-1.5 rounded-lg transition-colors hover:text-zinc-900">
            ← New upload
          </button>
        </div>
      </div>

      {data.status === 'error' && <ErrorBanner message={data.error_message} />}

      {/* Profile header */}
      <Card className="mb-4 flex items-start gap-5">
        <div className="w-14 h-14 rounded-full bg-violet-100 text-violet-700 flex items-center justify-center
          font-mono text-base font-medium shrink-0">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-display text-xl font-light text-zinc-900">
            {profile?.name || r?.name || 'Unknown'}
          </h3>
          {profile?.login && (
            <p className="text-xs font-mono text-zinc-500 mt-0.5">
              @{profile.login} ·{' '}
              <a href={`https://github.com/${profile.login}`} target="_blank" rel="noreferrer"
                className="underline underline-offset-2 hover:text-zinc-700">
                github.com/{profile.login}
              </a>
            </p>
          )}
          {profile?.bio && <p className="text-xs font-mono text-zinc-500 mt-1">{truncate(profile.bio, 120)}</p>}
          <div className="flex flex-wrap gap-3 mt-2">
            {profile?.location && <Meta val={`📍 ${profile.location}`} />}
            {profile?.company  && <Meta val={`🏢 ${profile.company}`} />}
            {r?.email          && <Meta val={`✉ ${r.email}`} />}
          </div>
        </div>
        <div className="shrink-0 pl-4 border-l border-zinc-100">
          <ScoreRing score={developer_score} grade={score_grade} gradeClass={gradeClass} />
        </div>
      </Card>

      {/* Parsed resume strip */}
      <div className="bg-zinc-50 border border-zinc-100 rounded-2xl p-4 mb-4
        grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
        <Field label="name"       val={r?.name} />
        <Field label="email"      val={r?.email} />
        <Field label="experience" val={r?.years_of_experience ? `${r.years_of_experience} yrs` : null} />
        <Field label="skills"     val={r?.skills?.slice(0,5).join(', ')} />
      </div>

      {/* GitHub stats grid */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-4">
        <MetricCard label="Repositories" value={fmt(profile?.public_repos)} />
        <MetricCard label="Total Stars"  value={fmt(gh?.total_stars)} />
        <MetricCard label="Total Forks"  value={fmt(gh?.total_forks)} />
        <MetricCard label="Followers"    value={fmt(profile?.followers)} />
        <MetricCard label="Following"    value={fmt(profile?.following)} />
        <MetricCard label="Last Active"  value={gh?.last_active ? timeAgo(gh.last_active) : '–'} />
      </div>

      {/* AI Insight */}
      {ai_insight && (
        <Card className="mb-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-violet-400 shrink-0" />
            <SectionTitle>AI-generated insight</SectionTitle>
          </div>
          <p className="font-display text-base font-light text-zinc-800 leading-relaxed italic">
            {ai_insight}
          </p>
        </Card>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <Card>
          <SectionTitle>Language distribution</SectionTitle>
          <LanguageChart distribution={gh?.language_distribution} />
        </Card>
        <Card>
          <SectionTitle>Commit activity · 12 months</SectionTitle>
          <ActivityTimeline commitActivity={gh?.commit_activity} />
        </Card>
      </div>

      {/* Top repos + skills */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <Card>
          <SectionTitle>Top repositories</SectionTitle>
          <div className="space-y-3">
            {gh?.repositories?.slice(0,6).map(repo => (
              <RepoRow key={repo.name} repo={repo} login={profile?.login} />
            ))}
            {!gh?.repositories?.length && <p className="text-xs text-zinc-400 font-mono">No repositories.</p>}
          </div>
        </Card>
        <Card>
          <SectionTitle>Extracted skills</SectionTitle>
          <div className="flex flex-wrap gap-2 mb-4">
            {r?.skills?.map(s => (
              <span key={s} className="px-2.5 py-1 bg-zinc-100 text-zinc-700 text-xs font-mono rounded-lg border border-zinc-200">{s}</span>
            ))}
            {!r?.skills?.length && <p className="text-xs text-zinc-400 font-mono">No skills extracted.</p>}
          </div>
          {r?.experience?.length > 0 && (
            <>
              <SectionTitle>Experience</SectionTitle>
              {r.experience.slice(0,3).map((e, i) => (
                <div key={i} className="mb-2">
                  <p className="text-xs font-mono font-medium text-zinc-800">{e.role} <span className="text-zinc-400">at</span> {e.company}</p>
                  {e.duration && <p className="text-[10px] font-mono text-zinc-400">{e.duration}</p>}
                </div>
              ))}
            </>
          )}
        </Card>
      </div>

      {/* Job compatibility CTA */}
      <Card className="bg-zinc-900 border-zinc-900 text-white">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <p className="font-mono font-medium text-sm text-white mb-1">Job compatibility scoring</p>
            <p className="text-xs font-mono text-zinc-400">Match this candidate against job descriptions to compute fit scores.</p>
          </div>
          <button onClick={() => onNavigate('jobs')}
            className="px-4 py-2 bg-white text-zinc-900 rounded-lg text-xs font-mono hover:bg-zinc-100 transition-colors shrink-0">
            Go to Jobs →
          </button>
        </div>
      </Card>
    </div>
  )
}

const Meta = ({ val }) => <span className="text-[11px] font-mono text-zinc-400">{val}</span>
const Field = ({ label, val }) => (
  <div>
    <p className="text-[10px] text-zinc-400 uppercase tracking-wide mb-0.5">{label}</p>
    <p className="text-zinc-700 truncate">{val || '–'}</p>
  </div>
)
const RepoRow = ({ repo, login }) => (
  <div className="flex items-start justify-between gap-2">
    <div className="min-w-0">
      <a href={repo.html_url || `https://github.com/${login}/${repo.name}`}
         target="_blank" rel="noreferrer"
         className="text-xs font-mono text-zinc-900 hover:underline underline-offset-2 truncate block">
        {repo.name}
      </a>
      {repo.description && (
        <p className="text-[11px] font-mono text-zinc-400 mt-0.5 truncate">{truncate(repo.description, 55)}</p>
      )}
      {repo.language && <span className="text-[10px] font-mono text-zinc-400">{repo.language}</span>}
    </div>
    <div className="flex gap-3 shrink-0 text-[11px] font-mono text-zinc-400">
      <span>★ {fmt(repo.stargazers_count)}</span>
      <span>⑂ {fmt(repo.forks_count)}</span>
    </div>
  </div>
)
