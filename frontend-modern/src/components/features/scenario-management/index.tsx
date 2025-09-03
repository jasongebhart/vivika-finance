'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Trash2,
  Merge,
  Filter,
  Search,
  ChevronDown,
  ChevronRight,
  Clock,
  Users,
  Home,
  GraduationCap,
  MapPin
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { useScenarios } from '@/hooks/use-scenarios'
import { formatCurrency } from '@/lib/utils'

interface ScenarioGroup {
  baseConfig: string
  scenarios: any[]
  maxDuration: number
  totalAssets?: number
}

function parseScenarioName(name: string) {
  const parts = name.split(' ')
  return {
    location: parts[0], // Mn, Sd, Sf
    people: parts.slice(1, 3).join(' '), // Hav Jason
    status1: parts[3], // First person status
    status2: parts[4], // Second person status  
    housing: parts[5], // Own, Rent
    schoolType: parts[6], // Private, Public, Pripub
    duration: parts[7], // 2yrs, 4yrs, etc.
    extras: parts.slice(8).join(' ') // Any additional info
  }
}

function getBaseConfig(scenario: any) {
  const parsed = parseScenarioName(scenario.name)
  return `${parsed.location} ${parsed.people} ${parsed.status1} ${parsed.status2} ${parsed.housing} ${parsed.schoolType} ${parsed.extras}`.trim()
}

function ScenarioGroupCard({ group, onDeleteScenarios, onMergeScenarios }: {
  group: ScenarioGroup
  onDeleteScenarios: (scenarioIds: string[]) => void
  onMergeScenarios: (scenarios: any[], keepLongest: boolean) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])

  const sortedScenarios = [...group.scenarios].sort((a, b) => {
    const aDuration = parseInt(parseScenarioName(a.name).duration?.replace('yrs', '') || '0')
    const bDuration = parseInt(parseScenarioName(b.name).duration?.replace('yrs', '') || '0')
    return aDuration - bDuration
  })

  const handleSelectScenario = (scenarioId: string, checked: boolean) => {
    if (checked) {
      setSelectedScenarios([...selectedScenarios, scenarioId])
    } else {
      setSelectedScenarios(selectedScenarios.filter(id => id !== scenarioId))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedScenarios(group.scenarios.map(s => s.id))
    } else {
      setSelectedScenarios([])
    }
  }

  const canStreamline = group.scenarios.length > 1

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
            <div>
              <CardTitle className="text-lg">{group.baseConfig}</CardTitle>
              <CardDescription>
                {group.scenarios.length} scenarios • Max duration: {group.maxDuration} years
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {group.totalAssets && (
              <span className="text-sm font-medium text-muted-foreground">
                {formatCurrency(group.totalAssets)}
              </span>
            )}
            <Badge variant={canStreamline ? "destructive" : "secondary"}>
              {canStreamline ? 'Duplicate' : 'Unique'}
            </Badge>
          </div>
        </div>
      </CardHeader>

      {expanded && (
        <CardContent>
          <div className="space-y-4">
            {/* Bulk Actions */}
            {canStreamline && (
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center space-x-4">
                  <Checkbox
                    checked={selectedScenarios.length === group.scenarios.length}
                    onCheckedChange={handleSelectAll}
                  />
                  <span className="text-sm font-medium">
                    {selectedScenarios.length > 0 
                      ? `${selectedScenarios.length} selected`
                      : 'Select all scenarios'
                    }
                  </span>
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onMergeScenarios(
                      group.scenarios.filter(s => selectedScenarios.includes(s.id)),
                      true
                    )}
                    disabled={selectedScenarios.length < 2}
                  >
                    <Merge className="h-4 w-4 mr-2" />
                    Keep Longest
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => onDeleteScenarios(selectedScenarios)}
                    disabled={selectedScenarios.length === 0}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Selected
                  </Button>
                </div>
              </div>
            )}

            {/* Scenario List */}
            <div className="space-y-2">
              {sortedScenarios.map((scenario) => {
                const parsed = parseScenarioName(scenario.name)
                const duration = parseInt(parsed.duration?.replace('yrs', '') || '0')
                
                return (
                  <div
                    key={scenario.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex items-center space-x-3">
                      {canStreamline && (
                        <Checkbox
                          checked={selectedScenarios.includes(scenario.id)}
                          onCheckedChange={(checked) => handleSelectScenario(scenario.id, !!checked)}
                        />
                      )}
                      <div>
                        <p className="font-medium">{scenario.name}</p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {duration} years
                          </span>
                          <span className="flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {parsed.location}
                          </span>
                          <span className="flex items-center">
                            <Users className="h-3 w-3 mr-1" />
                            {parsed.status1}/{parsed.status2}
                          </span>
                          <span className="flex items-center">
                            <Home className="h-3 w-3 mr-1" />
                            {parsed.housing}
                          </span>
                          <span className="flex items-center">
                            <GraduationCap className="h-3 w-3 mr-1" />
                            {parsed.schoolType}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(scenario.created_at).toLocaleDateString()}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  )
}

export function ScenarioManagement() {
  const { scenarios, isLoading, deleteScenario } = useScenarios()
  const [searchTerm, setSearchTerm] = useState('')
  const [showDuplicatesOnly, setShowDuplicatesOnly] = useState(true)
  const [scenarioGroups, setScenarioGroups] = useState<ScenarioGroup[]>([])

  useEffect(() => {
    if (scenarios.length === 0) return

    // Group scenarios by their base configuration
    const groups = new Map<string, ScenarioGroup>()

    scenarios.forEach((scenario) => {
      const baseConfig = getBaseConfig(scenario)
      const parsed = parseScenarioName(scenario.name)
      const duration = parseInt(parsed.duration?.replace('yrs', '') || '0')

      if (!groups.has(baseConfig)) {
        groups.set(baseConfig, {
          baseConfig,
          scenarios: [],
          maxDuration: 0
        })
      }

      const group = groups.get(baseConfig)!
      group.scenarios.push(scenario)
      group.maxDuration = Math.max(group.maxDuration, duration)

      // Try to get total assets from first scenario
      if (group.scenarios.length === 1) {
        try {
          const userData = JSON.parse(scenario.user_data || '{}')
          if (userData.assets) {
            group.totalAssets = userData.assets.filter((asset: any) => 
              !asset.name?.toLowerCase().includes('principal') && 
              !asset.name?.toLowerCase().includes('total') && 
              !asset.name?.toLowerCase().includes('summary')
            ).reduce((sum: number, asset: any) => 
              sum + (asset.current_value || 0), 0
            )
          }
        } catch (error) {
          console.warn('Could not parse assets for scenario:', scenario.id)
        }
      }
    })

    const groupArray = Array.from(groups.values())
      .sort((a, b) => b.scenarios.length - a.scenarios.length) // Sort by number of duplicates

    setScenarioGroups(groupArray)
  }, [scenarios])

  const filteredGroups = scenarioGroups.filter(group => {
    const matchesSearch = group.baseConfig.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = !showDuplicatesOnly || group.scenarios.length > 1
    return matchesSearch && matchesFilter
  })

  const handleDeleteScenarios = async (scenarioIds: string[]) => {
    if (confirm(`Are you sure you want to delete ${scenarioIds.length} scenarios? This cannot be undone.`)) {
      for (const id of scenarioIds) {
        await deleteScenario(id)
      }
    }
  }

  const handleMergeScenarios = async (scenarios: any[], keepLongest: boolean) => {
    if (keepLongest) {
      // Sort by duration and keep only the longest
      const sorted = scenarios.sort((a, b) => {
        const aDuration = parseInt(parseScenarioName(a.name).duration?.replace('yrs', '') || '0')
        const bDuration = parseInt(parseScenarioName(b.name).duration?.replace('yrs', '') || '0')
        return bDuration - aDuration
      })
      
      const toDelete = sorted.slice(1).map(s => s.id)
      if (toDelete.length > 0) {
        await handleDeleteScenarios(toDelete)
      }
    }
  }

  const totalScenarios = scenarios.length
  const duplicateGroups = scenarioGroups.filter(g => g.scenarios.length > 1).length
  const potentialSavings = scenarioGroups.reduce((sum, group) => 
    sum + Math.max(0, group.scenarios.length - 1), 0
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Scenario Management
            </h1>
            <p className="text-muted-foreground">
              Streamline duplicate scenarios and manage your financial planning library
            </p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold">{totalScenarios}</div>
              <p className="text-xs text-muted-foreground">Total Scenarios</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-orange-600">{duplicateGroups}</div>
              <p className="text-xs text-muted-foreground">Groups with Duplicates</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-red-600">{potentialSavings}</div>
              <p className="text-xs text-muted-foreground">Scenarios to Remove</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-green-600">{totalScenarios - potentialSavings}</div>
              <p className="text-xs text-muted-foreground">After Cleanup</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1 max-w-md">
            <Input
              placeholder="Search scenario configurations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="duplicates-only"
              checked={showDuplicatesOnly}
              onCheckedChange={setShowDuplicatesOnly}
            />
            <label htmlFor="duplicates-only" className="text-sm font-medium">
              Show duplicates only
            </label>
          </div>
        </div>

        {/* Scenario Groups */}
        <div className="space-y-4">
          {filteredGroups.map((group, index) => (
            <motion.div
              key={group.baseConfig}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <ScenarioGroupCard
                group={group}
                onDeleteScenarios={handleDeleteScenarios}
                onMergeScenarios={handleMergeScenarios}
              />
            </motion.div>
          ))}
        </div>

        {filteredGroups.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {showDuplicatesOnly 
                ? 'No duplicate scenarios found. All scenarios are unique!'
                : 'No scenarios match your search criteria.'
              }
            </p>
          </div>
        )}
      </main>
    </div>
  )
}