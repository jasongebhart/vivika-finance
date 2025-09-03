'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ErrorBoundary } from '@/components/error-boundary'
import { ScenarioManagement } from '@/components/features/scenario-management/scenario-management'
import { ScenarioComparison } from '@/components/features/scenario-comparison/scenario-comparison'

export default function ScenarioManagementPage() {
  const router = useRouter()
  const [showComparison, setShowComparison] = useState(false)
  const [comparisonScenarios, setComparisonScenarios] = useState<any[]>([])

  const handleScenarioSelect = (scenario: any) => {
    // Navigate to scenario builder with pre-filled data
    router.push('/scenario-builder')
  }

  const handleCompareScenarios = (scenarios: any[]) => {
    // Convert to comparison format
    const formattedScenarios = scenarios.map(s => ({
      id: s.id,
      name: s.name,
      location: s.location,
      spouse1Status: s.spouse1_status,
      spouse2Status: s.spouse2_status,
      housing: s.housing,
      schoolType: s.school_type,
      projectionYears: s.projection_years,
      projectedNetWorth: s.projection_results?.final_net_worth
    }))
    
    setComparisonScenarios(formattedScenarios)
    setShowComparison(true)
  }

  if (showComparison) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-background">
          <header className="border-b border bg-card">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">
                    Scenario Comparison
                  </h1>
                  <p className="text-muted-foreground">
                    Compare your selected financial scenarios
                  </p>
                </div>
              </div>
            </div>
          </header>

          <main className="container mx-auto px-6 py-8">
            <ScenarioComparison
              scenarios={comparisonScenarios}
              onBack={() => setShowComparison(false)}
            />
          </main>
        </div>
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        <header className="border-b border bg-card">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground">
                  Scenario Management
                </h1>
                <p className="text-muted-foreground">
                  Manage and compare your financial planning scenarios
                </p>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8">
          <ScenarioManagement
            onScenarioSelect={handleScenarioSelect}
            onCompareScenarios={handleCompareScenarios}
          />
        </main>
      </div>
    </ErrorBoundary>
  )
}