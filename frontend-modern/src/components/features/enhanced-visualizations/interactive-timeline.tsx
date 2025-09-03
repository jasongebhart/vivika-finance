'use client'

import { useState, useMemo, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Calendar, 
  DollarSign,
  Home,
  GraduationCap,
  Car,
  Heart,
  Briefcase,
  Baby
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  ComposedChart,
  Bar,
  ReferenceLine,
  Brush
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface TimelineEvent {
  year: number
  age: number
  type: 'milestone' | 'expense' | 'income' | 'decision'
  category: 'housing' | 'education' | 'career' | 'family' | 'health' | 'financial'
  title: string
  description: string
  amount?: number
  impact: 'positive' | 'negative' | 'neutral'
}

interface InteractiveTimelineProps {
  data: {
    scenarios: Array<{
      id: string
      name: string
      results: {
        yearly_projections?: Array<{
          year: number
          age: number
          net_worth: number
          income: number
          expenses: number
          net_cash_flow: number
        }>
      }
      parameters: {
        location: string
        housing: string
        schoolType: string
        spouse1Status: string
        spouse2Status: string
      }
    }>
  }
  className?: string
}

export function InteractiveTimelineVisualization({ data, className = '' }: InteractiveTimelineProps) {
  const [currentYear, setCurrentYear] = useState(2025)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1000) // ms per year
  const [selectedScenario, setSelectedScenario] = useState(data.scenarios[0]?.id || '')
  const [showEvents, setShowEvents] = useState(true)
  const [eventFilter, setEventFilter] = useState<string[]>([])

  // Generate timeline events based on scenario parameters
  const timelineEvents = useMemo((): TimelineEvent[] => {
    const events: TimelineEvent[] = []
    const currentAge = 52 // Base age
    
    // Housing events
    events.push({
      year: 2025,
      age: currentAge,
      type: 'decision',
      category: 'housing',
      title: 'Housing Decision',
      description: `Current housing: ${data.scenarios[0]?.parameters.housing || 'Unknown'}`,
      impact: 'neutral'
    })

    // Education events (kids college)
    events.push({
      year: 2030,
      age: currentAge + 5,
      type: 'expense',
      category: 'education',
      title: 'Tate Starts College',
      description: 'First child begins college education',
      amount: 75000,
      impact: 'negative'
    })

    events.push({
      year: 2033,
      age: currentAge + 8,
      type: 'expense',
      category: 'education',
      title: 'Wynn Starts College',
      description: 'Second child begins college education',
      amount: 75000,
      impact: 'negative'
    })

    // Career milestones
    events.push({
      year: 2027,
      age: currentAge + 2,
      type: 'milestone',
      category: 'career',
      title: 'Career Peak',
      description: 'Reaching maximum earning potential',
      amount: 500000,
      impact: 'positive'
    })

    events.push({
      year: 2030,
      age: currentAge + 5,
      type: 'decision',
      category: 'career',
      title: 'Potential Relocation',
      description: 'Considering move to different location',
      impact: 'neutral'
    })

    // Retirement planning
    events.push({
      year: 2035,
      age: currentAge + 10,
      type: 'milestone',
      category: 'financial',
      title: 'Early Retirement Option',
      description: 'Financially ready for early retirement',
      amount: 5000000,
      impact: 'positive'
    })

    // Health and family
    events.push({
      year: 2028,
      age: currentAge + 3,
      type: 'expense',
      category: 'health',
      title: 'Healthcare Premium Increase',
      description: 'Age-related healthcare cost increases',
      amount: 15000,
      impact: 'negative'
    })

    events.push({
      year: 2026,
      age: currentAge + 1,
      type: 'milestone',
      category: 'family',
      title: 'Empty Nest Preparation',
      description: 'Kids becoming more independent',
      impact: 'neutral'
    })

    return events.sort((a, b) => a.year - b.year)
  }, [data.scenarios])

  // Timeline data with events integrated
  const timelineData = useMemo(() => {
    const scenario = data.scenarios.find(s => s.id === selectedScenario)
    if (!scenario || !scenario.results.yearly_projections) return []

    return scenario.results.yearly_projections.map(projection => {
      const yearEvents = timelineEvents.filter(event => event.year === projection.year)
      
      return {
        ...projection,
        events: yearEvents,
        hasEvents: yearEvents.length > 0,
        eventImpact: yearEvents.reduce((total, event) => {
          if (event.impact === 'positive') return total + (event.amount || 0)
          if (event.impact === 'negative') return total - (event.amount || 0)
          return total
        }, 0)
      }
    })
  }, [selectedScenario, data.scenarios, timelineEvents])

  // Auto-play functionality
  const playTimeline = useCallback(() => {
    if (!isPlaying) return

    const maxYear = Math.max(...timelineData.map(d => d.year))
    const nextYear = currentYear + 1

    if (nextYear <= maxYear) {
      setCurrentYear(nextYear)
    } else {
      setIsPlaying(false)
      setCurrentYear(timelineData[0]?.year || 2025)
    }
  }, [isPlaying, currentYear, timelineData])

  // Auto-advance timeline
  useState(() => {
    if (isPlaying) {
      const timer = setTimeout(playTimeline, playbackSpeed)
      return () => clearTimeout(timer)
    }
  })

  const currentData = timelineData.find(d => d.year === currentYear)
  const currentEvents = currentData?.events || []

  const getEventIcon = (category: string) => {
    switch (category) {
      case 'housing': return <Home className="h-4 w-4" />
      case 'education': return <GraduationCap className="h-4 w-4" />
      case 'career': return <Briefcase className="h-4 w-4" />
      case 'family': return <Baby className="h-4 w-4" />
      case 'health': return <Heart className="h-4 w-4" />
      case 'financial': return <DollarSign className="h-4 w-4" />
      default: return <Calendar className="h-4 w-4" />
    }
  }

  const getEventColor = (impact: string) => {
    switch (impact) {
      case 'positive': return 'text-green-600 bg-green-100'
      case 'negative': return 'text-red-600 bg-red-100'
      default: return 'text-blue-600 bg-blue-100'
    }
  }

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff88']

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Timeline Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Interactive Financial Timeline
            </span>
            <Badge variant="outline" className="text-lg">
              {currentYear} (Age {currentData?.age || 52})
            </Badge>
          </CardTitle>
          <CardDescription>
            Explore your financial journey through time with interactive controls
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Playback Controls */}
          <div className="flex items-center justify-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentYear(Math.max(2025, currentYear - 1))}
            >
              <SkipBack className="h-4 w-4" />
            </Button>
            
            <Button
              variant={isPlaying ? "secondary" : "default"}
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {isPlaying ? 'Pause' : 'Play'}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentYear(Math.min(2035, currentYear + 1))}
            >
              <SkipForward className="h-4 w-4" />
            </Button>
          </div>

          {/* Timeline Scrubber */}
          <div className="space-y-2">
            <Slider
              value={[currentYear]}
              onValueChange={(value) => setCurrentYear(value[0])}
              min={2025}
              max={2035}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>2025</span>
              <span>2030</span>
              <span>2035</span>
            </div>
          </div>

          {/* Scenario Selector */}
          <div className="flex space-x-2">
            {data.scenarios.map(scenario => (
              <Button
                key={scenario.id}
                variant={selectedScenario === scenario.id ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedScenario(scenario.id)}
              >
                {scenario.name}
              </Button>
            ))}
          </div>

          {/* Speed Control */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Playback Speed</label>
            <Slider
              value={[playbackSpeed]}
              onValueChange={(value) => setPlaybackSpeed(value[0])}
              min={200}
              max={2000}
              step={200}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Fast (0.2s)</span>
              <span>Slow (2s)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Year Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(currentData?.net_worth || 0)}
              </div>
              <div className="text-sm text-muted-foreground">Net Worth</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(currentData?.income || 0)}
              </div>
              <div className="text-sm text-muted-foreground">Annual Income</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(currentData?.expenses || 0)}
              </div>
              <div className="text-sm text-muted-foreground">Annual Expenses</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className={`text-2xl font-bold ${
                (currentData?.net_cash_flow || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(currentData?.net_cash_flow || 0)}
              </div>
              <div className="text-sm text-muted-foreground">Net Cash Flow</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Evolution Timeline</CardTitle>
          <CardDescription>
            Financial progression with key life events highlighted
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="year" 
                className="text-xs"
              />
              <YAxis 
                yAxisId="left"
                tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                className="text-xs"
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                className="text-xs"
              />
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-background border rounded-lg p-4 shadow-lg max-w-sm">
                        <p className="font-medium mb-2">Year {label} (Age {data.age})</p>
                        <div className="space-y-1 text-sm">
                          <p>Net Worth: {formatCurrency(data.net_worth)}</p>
                          <p>Income: {formatCurrency(data.income)}</p>
                          <p>Expenses: {formatCurrency(data.expenses)}</p>
                          <p>Cash Flow: {formatCurrency(data.net_cash_flow)}</p>
                        </div>
                        {data.events.length > 0 && (
                          <div className="mt-2 pt-2 border-t">
                            <p className="font-medium text-xs">Events:</p>
                            {data.events.map((event: TimelineEvent, i: number) => (
                              <p key={i} className="text-xs text-muted-foreground">
                                • {event.title}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  }
                  return null
                }}
              />
              
              {/* Net Worth Area */}
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="net_worth"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              
              {/* Cash Flow Bars */}
              <Bar
                yAxisId="right"
                dataKey="net_cash_flow"
                fill="#82ca9d"
                opacity={0.6}
              />
              
              {/* Current Year Indicator */}
              <ReferenceLine 
                x={currentYear} 
                stroke="#ff7300" 
                strokeWidth={3}
                strokeDasharray="5 5"
              />
              
              {/* Event Markers */}
              {timelineData
                .filter(d => d.hasEvents)
                .map((d, i) => (
                  <ReferenceLine
                    key={i}
                    x={d.year}
                    stroke="#ff0000"
                    strokeOpacity={0.5}
                    strokeDasharray="2 2"
                  />
                ))
              }
              
              {/* Brush for navigation */}
              <Brush
                dataKey="year"
                height={30}
                stroke="#8884d8"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Current Year Events */}
      {currentEvents.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Life Events in {currentYear}</CardTitle>
            <CardDescription>
              Important milestones and decisions for this year
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {currentEvents.map((event, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 p-3 rounded-lg ${getEventColor(event.impact)}`}
                >
                  <div className="flex-shrink-0">
                    {getEventIcon(event.category)}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">{event.title}</h4>
                    <p className="text-sm opacity-90">{event.description}</p>
                    {event.amount && (
                      <p className="text-sm font-medium mt-1">
                        {event.impact === 'positive' ? '+' : ''}
                        {formatCurrency(event.amount)}
                      </p>
                    )}
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {event.type}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Event Timeline Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Complete Event Timeline</CardTitle>
          <CardDescription>
            All major life events and financial milestones
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border"></div>
            
            {/* Events */}
            <div className="space-y-6">
              {timelineEvents.map((event, index) => (
                <div key={index} className="relative flex items-start space-x-4">
                  {/* Event dot */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full border-2 ${
                    event.year === currentYear 
                      ? 'border-orange-500 bg-orange-100' 
                      : 'border-gray-300 bg-gray-100'
                  } flex items-center justify-center`}>
                    {getEventIcon(event.category)}
                  </div>
                  
                  {/* Event content */}
                  <div className="flex-1 pb-6">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium">{event.title}</h4>
                      <Badge variant="outline">{event.year}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {event.description}
                    </p>
                    {event.amount && (
                      <p className={`text-sm font-medium ${
                        event.impact === 'positive' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {event.impact === 'positive' ? '+' : ''}
                        {formatCurrency(event.amount)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}