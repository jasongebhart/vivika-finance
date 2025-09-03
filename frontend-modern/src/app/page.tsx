import { Dashboard } from '@/components/features/dashboard'
import { ErrorBoundary } from '@/components/error-boundary'

export default function HomePage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-slate-100 p-4">
        <Dashboard />
      </div>
    </ErrorBoundary>
  )
}
