'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Calendar,
  Users,
  Home,
  GraduationCap,
  MapPin,
  ArrowRight,
  BarChart3,
  Activity,
  Target
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { formatCurrency } from '@/lib/utils'
import { getAPIUrl } from '@/lib/config'

interface ScenarioConfiguration {
  id: string
  name: string
  location: string
  spouse1Status: string
  spouse2Status: string
  housing: string
  schoolType: string
  projectionYears: number
  projectedNetWorth?: number
  isRunning?: boolean
}

interface ComparisonMetrics {
  net_worth_projections: Record<string, {
    final_net_worth: number
    growth_rate: number
    key_factors: string[]
  }>
  key_differences: string[]
  recommendations: string[]
}

interface ComparisonResults {
  scenarios: ScenarioConfiguration[]
  comparison_timestamp: string
  metrics: ComparisonMetrics
}

interface ScenarioComparisonProps {
  scenarios: ScenarioConfiguration[]
  onBack?: () => void
  className?: string
}

export function ScenarioComparison({ 
  scenarios, 
  onBack,
  className = '' 
}: ScenarioComparisonProps) {
  const [comparisonResults, setComparisonResults] = useState<ComparisonResults | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (scenarios.length > 0) {
      generateComparison()
    }
  }, [scenarios])

  const generateComparison = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // In a real implementation, this would call the API
      const response = await fetch(getAPIUrl('/api/scenarios/compare'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scenarios }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate comparison')
      }

      const results = await response.json()
      setComparisonResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const getParameterIcon = (param: string) => {
    switch (param) {
      case 'location': return <MapPin className="h-4 w-4" />
      case 'housing': return <Home className="h-4 w-4" />
      case 'education': return <GraduationCap className="h-4 w-4" />
      case 'status': return <Users className="h-4 w-4" />
      case 'years': return <Calendar className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getStatusBadgeVariant = (status1: string, status2: string) => {
    if (status1 === 'Work' && status2 === 'Work') return 'default'
    if (status1 === 'Retired' && status2 === 'Retired') return 'secondary'
    return 'outline'
  }

  const getBestPerformingScenario = () => {
    if (!comparisonResults) return null
    
    let bestScenario = null
    let highestNetWorth = 0

    Object.entries(comparisonResults.metrics.net_worth_projections).forEach(([name, metrics]) => {
      if (metrics.final_net_worth > highestNetWorth) {
        highestNetWorth = metrics.final_net_worth
        bestScenario = name
      }
    })

    return bestScenario
  }

  if (isLoading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Generating scenario comparison...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-red-500 mb-4">
              <Activity className="h-8 w-8 mx-auto mb-2" />
              <p className="font-medium">Comparison Failed</p>
            </div>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={generateComparison} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const bestScenario = getBestPerformingScenario()

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Scenario Comparison
              </CardTitle>
              <CardDescription>
                Comparing {scenarios.length} financial scenarios
              </CardDescription>
            </div>
            {onBack && (
              <Button onClick={onBack} variant="outline">
                Back to Builder
              </Button>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {scenarios.map((scenario, index) => {
          const isTop = scenario.name === bestScenario
          const projection = comparisonResults?.metrics.net_worth_projections[scenario.name]
          
          return (
            <motion.div
              key={scenario.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className={`relative ${isTop ? 'ring-2 ring-primary' : ''}`}>
                {isTop && (
                  <Badge className="absolute -top-2 left-4 bg-primary">
                    Best Performance
                  </Badge>
                )}
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">
                    Scenario {index + 1}
                  </CardTitle>
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <Badge variant="outline" className="text-xs">
                      {scenario.location}
                    </Badge>
                    <Badge 
                      variant={getStatusBadgeVariant(scenario.spouse1Status, scenario.spouse2Status)}
                      className="text-xs"
                    >
                      {scenario.spouse1Status[0]}/{scenario.spouse2Status[0]}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center text-xs">
                      <Home className="h-3 w-3 mr-1" />
                      {scenario.housing}
                    </div>
                    <div className="flex items-center text-xs">
                      <GraduationCap className="h-3 w-3 mr-1" />
                      {scenario.schoolType}
                    </div>
                    <div className="flex items-center text-xs">
                      <Calendar className="h-3 w-3 mr-1" />
                      {scenario.projectionYears} years
                    </div>
                  </div>
                  
                  {projection && (
                    <div className="pt-2 border-t">
                      <div className="text-lg font-bold text-primary">
                        {formatCurrency(projection.final_net_worth)}
                      </div>
                      <div className="flex items-center text-xs text-muted-foreground">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        {(projection.growth_rate * 100).toFixed(1)}% growth
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Detailed Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Net Worth Projections</CardTitle>
          <CardDescription>
            Final projected net worth after {scenarios[0]?.projectionYears || 8} years
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {comparisonResults && Object.entries(comparisonResults.metrics.net_worth_projections)
            .sort(([,a], [,b]) => b.final_net_worth - a.final_net_worth)
            .map(([scenarioName, metrics], index) => {
              const scenario = scenarios.find(s => s.name === scenarioName)
              const maxNetWorth = Math.max(...Object.values(comparisonResults.metrics.net_worth_projections).map(m => m.final_net_worth))
              const percentage = (metrics.final_net_worth / maxNetWorth) * 100
              
              return (
                <motion.div
                  key={scenarioName}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-medium text-sm">{scenario?.location} Scenario</div>
                        <div className="text-xs text-muted-foreground">
                          {scenario?.spouse1Status}/{scenario?.spouse2Status} • {scenario?.housing} • {scenario?.schoolType}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">
                        {formatCurrency(metrics.final_net_worth)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {(metrics.growth_rate * 100).toFixed(1)}% annual growth
                      </div>
                    </div>
                  </div>
                  <Progress value={percentage} className="h-2" />
                </motion.div>
              )
            })}
        </CardContent>
      </Card>

      {/* Key Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              Key Differences
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <MapPin className="h-4 w-4 mt-1 text-muted-foreground" />
                <div>
                  <div className="font-medium text-sm">Location Impact</div>
                  <div className="text-xs text-muted-foreground">
                    Cost of living variations significantly affect long-term projections
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Users className="h-4 w-4 mt-1 text-muted-foreground" />
                <div>
                  <div className="font-medium text-sm">Employment Status</div>
                  <div className="text-xs text-muted-foreground">
                    Working vs. retirement status affects income and savings patterns
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <GraduationCap className="h-4 w-4 mt-1 text-muted-foreground" />
                <div>
                  <div className="font-medium text-sm">Education Costs</div>
                  <div className="text-xs text-muted-foreground">
                    Private vs. public education creates substantial expense differences
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-sm text-green-700 dark:text-green-300">
                    Optimal Choice
                  </span>
                </div>
                <p className="text-xs text-green-600 dark:text-green-400">
                  {bestScenario} shows the highest projected net worth
                </p>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="font-medium text-sm text-blue-700 dark:text-blue-300">
                    Consider Trade-offs
                  </span>
                </div>
                <p className="text-xs text-blue-600 dark:text-blue-400">
                  Balance financial outcomes with lifestyle preferences and quality of life factors
                </p>
              </div>
              <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                  <span className="font-medium text-sm text-amber-700 dark:text-amber-300">
                    Regular Review
                  </span>
                </div>
                <p className="text-xs text-amber-600 dark:text-amber-400">
                  Update scenarios annually to reflect changing circumstances and market conditions
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}