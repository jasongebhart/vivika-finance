'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus,
  Trash2,
  Play,
  BarChart3,
  Edit,
  Filter,
  Search,
  Calendar,
  MapPin,
  Users,
  Home,
  GraduationCap,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { formatCurrency } from '@/lib/utils'
import { getAPIUrl } from '@/lib/config'

interface DynamicScenario {
  id: string
  name: string
  location: string
  spouse1_status: string
  spouse2_status: string
  housing: string
  school_type: string
  projection_years: number
  status: string
  created_at: string
  updated_at: string
  projection_results?: {
    final_net_worth: number
    annual_growth_rate: number
    total_expenses: number
    retirement_readiness: boolean
    calculated_at: string
  }
}

interface ScenarioManagementProps {
  className?: string
  onScenarioSelect?: (scenario: DynamicScenario) => void
  onCompareScenarios?: (scenarios: DynamicScenario[]) => void
}

export function ScenarioManagement({ 
  className = '',
  onScenarioSelect,
  onCompareScenarios
}: ScenarioManagementProps) {
  const [scenarios, setScenarios] = useState<DynamicScenario[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])

  // Load scenarios from database
  useEffect(() => {
    loadScenarios()
  }, [])

  const loadScenarios = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(getAPIUrl('/api/dynamic-scenarios?limit=100'))
      
      if (!response.ok) {
        throw new Error('Failed to load scenarios')
      }
      
      const data = await response.json()
      
      // Load full details for each scenario
      const scenariosWithDetails = await Promise.all(
        data.map(async (scenario: any) => {
          try {
            const detailResponse = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenario.id}`))
            if (detailResponse.ok) {
              return await detailResponse.json()
            }
            return scenario
          } catch (error) {
            console.error(`Failed to load details for scenario ${scenario.id}:`, error)
            return scenario
          }
        })
      )
      
      // Remove duplicates based on ID
      const uniqueScenarios = scenariosWithDetails.filter((scenario, index, self) => 
        index === self.findIndex(s => s.id === scenario.id)
      )
      
      setScenarios(uniqueScenarios)
    } catch (error) {
      console.error('Failed to load scenarios:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteScenario = async (scenarioId: string) => {
    try {
      const response = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenarioId}`), {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete scenario')
      }

      setScenarios(prev => prev.filter(s => s.id !== scenarioId))
      setSelectedScenarios(prev => prev.filter(id => id !== scenarioId))
    } catch (error) {
      console.error('Failed to delete scenario:', error)
    }
  }

  const handleRunScenario = async (scenario: DynamicScenario) => {
    try {
      // Validate scenario data
      if (!scenario.id) {
        throw new Error('Scenario ID is missing')
      }

      console.log('Running scenario:', scenario.id, scenario.name)

      // Update local state to show running
      setScenarios(prev => 
        prev.map(s => s.id === scenario.id ? { ...s, status: 'running' } : s)
      )

      const response = await fetch(getAPIUrl('/api/scenarios/run'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: scenario.id, name: scenario.name }),
      })

      console.log('Run scenario response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Run scenario error response:', errorText)
        throw new Error(`Failed to run scenario: ${response.status} ${errorText}`)
      }

      const result = await response.json()
      console.log('Scenario started running:', result)

      // Optionally reload scenarios to get updated status
      setTimeout(() => {
        loadScenarios()
      }, 2000)

    } catch (error) {
      console.error('Failed to run scenario:', error)
      alert(`Failed to run scenario: ${error instanceof Error ? error.message : 'Unknown error'}`)
      
      // Revert status on error
      setScenarios(prev => 
        prev.map(s => s.id === scenario.id ? { ...s, status: 'created' } : s)
      )
    }
  }

  const handleBulkDelete = async () => {
    const confirmed = window.confirm(`Are you sure you want to delete ${selectedScenarios.length} scenarios?`)
    if (!confirmed) return

    try {
      await Promise.all(
        selectedScenarios.map(id => 
          fetch(getAPIUrl(`/api/dynamic-scenarios/${id}`), { method: 'DELETE' })
        )
      )
      
      setScenarios(prev => prev.filter(s => !selectedScenarios.includes(s.id)))
      setSelectedScenarios([])
    } catch (error) {
      console.error('Failed to delete scenarios:', error)
    }
  }

  const handleCompareSelected = () => {
    const scenariosToCompare = scenarios.filter(s => selectedScenarios.includes(s.id))
    onCompareScenarios?.(scenariosToCompare)
  }

  const toggleScenarioSelection = (scenarioId: string) => {
    setSelectedScenarios(prev => 
      prev.includes(scenarioId)
        ? prev.filter(id => id !== scenarioId)
        : [...prev, scenarioId]
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running': return <Clock className="h-4 w-4 text-blue-500 animate-spin" />
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'default'
      case 'running': return 'secondary'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  // Filter scenarios
  const filteredScenarios = scenarios.filter(scenario => {
    const matchesSearch = scenario.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         scenario.location.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || scenario.status === statusFilter
    return matchesSearch && matchesStatus
  })

  if (isLoading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading scenarios...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Scenario Management
              </CardTitle>
              <CardDescription>
                Manage your financial planning scenarios
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              {selectedScenarios.length > 0 && (
                <>
                  <Button 
                    onClick={handleBulkDelete} 
                    variant="destructive" 
                    size="sm"
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete ({selectedScenarios.length})
                  </Button>
                  {selectedScenarios.length >= 2 && selectedScenarios.length <= 4 && (
                    <Button 
                      onClick={handleCompareSelected} 
                      variant="default" 
                      size="sm"
                    >
                      <BarChart3 className="h-4 w-4 mr-1" />
                      Compare ({selectedScenarios.length})
                    </Button>
                  )}
                </>
              )}
              <Button onClick={loadScenarios} variant="outline" size="sm">
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search scenarios..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border rounded px-3 py-2 text-sm"
              >
                <option value="all">All Status</option>
                <option value="created">Created</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scenarios Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <AnimatePresence>
          {filteredScenarios.map((scenario, index) => (
            <motion.div
              key={`mgmt-scenario-${scenario.id}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              layout
            >
              <Card 
                className={`hover:shadow-lg transition-shadow duration-200 cursor-pointer ${
                  selectedScenarios.includes(scenario.id) ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => toggleScenarioSelection(scenario.id)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-sm font-medium line-clamp-2">
                        {scenario.name}
                      </CardTitle>
                      <div className="flex items-center space-x-2 mt-2">
                        {getStatusIcon(scenario.status)}
                        <Badge variant={getStatusBadgeVariant(scenario.status)} className="text-xs">
                          {scenario.status}
                        </Badge>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={selectedScenarios.includes(scenario.id)}
                      onChange={() => toggleScenarioSelection(scenario.id)}
                      className="ml-2"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center">
                      <MapPin className="h-3 w-3 mr-1" />
                      {scenario.location}
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {scenario.projection_years}y
                    </div>
                    <div className="flex items-center">
                      <Users className="h-3 w-3 mr-1" />
                      {scenario.spouse1_status[0]}/{scenario.spouse2_status[0]}
                    </div>
                    <div className="flex items-center">
                      <Home className="h-3 w-3 mr-1" />
                      {scenario.housing}
                    </div>
                  </div>
                  
                  <div className="flex items-center text-xs">
                    <GraduationCap className="h-3 w-3 mr-1" />
                    {scenario.school_type}
                  </div>

                  {scenario.projection_results && (
                    <div className="pt-2 border-t">
                      <div className="text-lg font-bold text-primary">
                        {formatCurrency(scenario.projection_results.final_net_worth)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Projected Net Worth
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2">
                    <div className="text-xs text-muted-foreground">
                      {new Date(scenario.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex space-x-1">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRunScenario(scenario)
                        }}
                        size="sm"
                        variant="ghost"
                        disabled={scenario.status === 'running'}
                      >
                        <Play className="h-3 w-3" />
                      </Button>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          onScenarioSelect?.(scenario)
                        }}
                        size="sm"
                        variant="ghost"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteScenario(scenario.id)
                        }}
                        size="sm"
                        variant="ghost"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredScenarios.length === 0 && !isLoading && (
        <Card>
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No scenarios found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || statusFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria.' 
                : 'Create your first scenario to get started.'}
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Scenario
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}