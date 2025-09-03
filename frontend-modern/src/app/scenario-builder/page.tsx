'use client'

import { ErrorBoundary } from '@/components/error-boundary'
import { DynamicScenarioBuilder } from '@/components/features/scenario-builder/dynamic-scenario-builder'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function ScenarioBuilderPage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border bg-card">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link href="/">
                  <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                    <ArrowLeft className="h-4 w-4" />
                    <span>Back to Dashboard</span>
                  </Button>
                </Link>
                <div>
                  <h1 className="text-3xl font-bold text-foreground">
                    Dynamic Scenario Builder
                  </h1>
                  <p className="text-muted-foreground">
                    Configure and compare financial scenarios with dynamic parameters
                  </p>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-8">
          <DynamicScenarioBuilder
            onScenarioCreate={(scenario) => {
              console.log('Scenario created:', scenario)
            }}
            onScenarioRun={(scenario) => {
              console.log('Scenario running:', scenario)
            }}
            onCompareScenarios={(scenarios) => {
              console.log('Comparing scenarios:', scenarios)
            }}
          />
        </main>
      </div>
    </ErrorBoundary>
  )
}