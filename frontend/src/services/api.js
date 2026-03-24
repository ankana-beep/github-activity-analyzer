import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', timeout: 30000 })

// ── Resume ────────────────────────────────────────────────────────────────────
export const uploadResume = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/resume/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  }).then(r => r.data)
}

export const getReport = (candidateId) =>
  api.get(`/resume/${candidateId}/report`).then(r => r.data)

// ── GitHub ────────────────────────────────────────────────────────────────────
export const getGithubActivity = (username) =>
  api.get(`/github/${username}`).then(r => r.data)

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const listJobs = () =>
  api.get('/jobs/').then(r => r.data)

export const createJob = (payload) =>
  api.post('/jobs/', payload).then(r => r.data)

export const deleteJob = (jobId) =>
  api.delete(`/jobs/${jobId}`)

export const computeCompatibility = (candidateId, jobId) =>
  api.post('/jobs/compatibility', { candidate_id: candidateId, job_id: jobId }).then(r => r.data)

// ── Reports ───────────────────────────────────────────────────────────────────
export const listCandidates = (limit = 20) =>
  api.get('/reports/', { params: { limit } }).then(r => r.data)

export const getDownloadUrl = (candidateId, jobId = null) => {
  const base = `/api/v1/reports/${candidateId}/download`
  return jobId ? `${base}?job_id=${jobId}` : base
}

export default api
