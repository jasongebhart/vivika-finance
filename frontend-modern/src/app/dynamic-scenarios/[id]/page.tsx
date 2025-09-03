'use client'

import { use } from 'react'
import { DynamicScenarioDetail } from '@/components/features/dynamic-scenario-detail'

interface PageProps {
  params: Promise<{
    id: string
  }>
}

export default function DynamicScenarioDetailPage({ params }: PageProps) {
  const { id } = use(params)
  return <DynamicScenarioDetail scenarioId={id} />
}