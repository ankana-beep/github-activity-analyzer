import { useState } from 'react'
import Header from './components/layout/Header.jsx'
import Sidebar from './components/layout/Sidebar.jsx'
import UploadPage from './pages/UploadPage.jsx'
import ProcessingPage from './pages/ProcessingPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import JobsPage from './pages/JobsPage.jsx'

/**
 * App-level state machine.
 * Pages: upload → processing → dashboard | jobs
 */
export default function App() {
  const [page, setPage]           = useState('upload')   // upload | processing | dashboard | jobs
  const [candidateId, setCandidateId] = useState(null)
  const [reportData, setReportData]   = useState(null)

  const handleUploadSuccess = (id) => { setCandidateId(id); setPage('processing') }
  const handleAnalysisComplete = (data) => { setReportData(data); setPage('dashboard') }
  const handleReset = () => { setCandidateId(null); setReportData(null); setPage('upload') }

  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col">
      <Header onLogoClick={handleReset} />
      <div className="flex flex-1">
        {(page === 'dashboard' || page === 'jobs') && (
          <Sidebar activePage={page} onNavigate={setPage} candidateId={candidateId} />
        )}
        <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8">
          {page === 'upload'      && <UploadPage onSuccess={handleUploadSuccess} />}
          {page === 'processing'  && (
            <ProcessingPage
              candidateId={candidateId}
              onComplete={handleAnalysisComplete}
              onError={handleReset}
            />
          )}
          {page === 'dashboard'   && (
            <DashboardPage data={reportData} onReset={handleReset} onNavigate={setPage} />
          )}
          {page === 'jobs'        && (
            <JobsPage candidateId={candidateId} reportData={reportData} />
          )}
        </main>
      </div>
    </div>
  )
}
