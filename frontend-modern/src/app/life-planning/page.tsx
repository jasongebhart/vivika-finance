import { LifePlanningDashboard } from '@/components/features/life-planning/life-planning-dashboard'

export default function LifePlanningPage() {
  return (
    <div className="container mx-auto py-8">
      <LifePlanningDashboard />
    </div>
  )
}

export const metadata = {
  title: 'Life Planning Dashboard',
  description: 'Analyze optimal timing for major life decisions: moving, education choices, and family planning',
}