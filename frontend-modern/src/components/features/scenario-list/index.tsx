'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Eye, 
  Edit, 
  Trash2, 
  Play,
  BarChart3,
  Calendar,
  DollarSign,
  TrendingUp
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/hooks/use-toast'
import { useScenarios } from '@/hooks/use-scenarios'
import { formatCurrency, formatPercentage, cn } from '@/lib/utils'
import type { Scenario } from '@/types'

// Correct birth dates
const HAVILAH_BIRTH_DATE = new Date('1974-07-15')
const JASON_BIRTH_DATE = new Date('1973-03-24')

// Calculate current ages
const calculateAge = (birthDate: Date) => {
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

interface ScenarioListProps {
  onScenarioSelect?: (scenario: Scenario) => void
  onCreateNew?: () => void
  onRunProjection?: (scenario: Scenario) => void
  onRunMonteCarlo?: (scenario: Scenario) => void
}

function ScenarioTypeIcon({ type }: { type: string }) {
  const iconClass = "h-4 w-4"
  
  switch (type) {
    case 'retirement':
      return <TrendingUp className={iconClass} />
    case 'relocation':
      return <Calendar className={iconClass} />
    case 'education':
      return <BarChart3 className={iconClass} />
    case 'major_purchase':
      return <DollarSign className={iconClass} />
    default:
      return <BarChart3 className={iconClass} />
  }
}

function ScenarioTypeLabel({ type }: { type: string }) {
  const labels = {
    current: 'Current Plan',
    retirement: 'Early Retirement',
    relocation: 'City Relocation',
    education: 'Education Planning',
    major_purchase: 'Major Purchase'
  }
  
  return labels[type as keyof typeof labels] || 'Unknown'
}

interface ScenarioCardProps {
  scenario: Scenario
  onSelect?: (scenario: Scenario) => void
  onRunProjection?: (scenario: Scenario) => void
  onRunMonteCarlo?: (scenario: Scenario) => void
  onEdit?: (scenario: Scenario) => void
  onDelete?: (scenario: Scenario) => void
  isSelectedForComparison?: boolean
  onComparisonToggle?: (scenarioId: string, selected: boolean) => void
}

function ScenarioCard({ 
  scenario, 
  onSelect, 
  onRunProjection, 
  onRunMonteCarlo, 
  onEdit, 
  onDelete,
  isSelectedForComparison = false,
  onComparisonToggle
}: ScenarioCardProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  
  const getTypeColor = (type: string) => {
    const colors = {
      current: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      retirement: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      relocation: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      education: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      major_purchase: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }
    return colors[type as keyof typeof colors] || colors.current
  }

  const yearsToRetirement = scenario.user_profile.retirement_age - scenario.user_profile.current_age
  const projectionYears = scenario.projection_settings.projection_years

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
    >
      <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              {onComparisonToggle && (
                <Checkbox
                  checked={isSelectedForComparison}
                  onCheckedChange={(checked) => onComparisonToggle(scenario.id, !!checked)}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
              <ScenarioTypeIcon type={scenario.scenario_type} />
              <CardTitle className="text-lg font-semibold">
                {scenario.name}
              </CardTitle>
            </div>
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation()
                  setIsMenuOpen(!isMenuOpen)
                }}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
              {isMenuOpen && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-background border border rounded-md shadow-lg z-10">
                  <div className="py-1">
                    <button
                      className="w-full text-left px-3 py-2 text-sm hover:bg-accent flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation()
                        onSelect?.(scenario)
                        setIsMenuOpen(false)
                      }}
                    >
                      <Eye className="h-4 w-4" />
                      <span>View Details</span>
                    </button>
                    <button
                      className="w-full text-left px-3 py-2 text-sm hover:bg-accent flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRunProjection?.(scenario)
                        setIsMenuOpen(false)
                      }}
                    >
                      <Play className="h-4 w-4" />
                      <span>Run Projection</span>
                    </button>
                    <button
                      className="w-full text-left px-3 py-2 text-sm hover:bg-accent flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRunMonteCarlo?.(scenario)
                        setIsMenuOpen(false)
                      }}
                    >
                      <BarChart3 className="h-4 w-4" />
                      <span>Monte Carlo</span>
                    </button>
                    <hr className="my-1" />
                    <button
                      className="w-full text-left px-3 py-2 text-sm hover:bg-accent flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation()
                        onEdit?.(scenario)
                        setIsMenuOpen(false)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                      <span>Edit</span>
                    </button>
                    <button
                      className="w-full text-left px-3 py-2 text-sm hover:bg-accent text-destructive flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDelete?.(scenario)
                        setIsMenuOpen(false)
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={cn("text-xs", getTypeColor(scenario.scenario_type))}>
              <ScenarioTypeLabel type={scenario.scenario_type} />
            </Badge>
            <span className="text-xs text-muted-foreground">
              Created {new Date(scenario.created_at).toLocaleDateString()}
            </span>
          </div>
        </CardHeader>
        <CardContent 
          className="pt-0 space-y-4"
          onClick={() => onSelect?.(scenario)}
        >
          <CardDescription className="line-clamp-2">
            {scenario.description || 'No description provided'}
          </CardDescription>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground">Current Ages</div>
              <div className="font-medium">{calculateAge(JASON_BIRTH_DATE)} / {calculateAge(HAVILAH_BIRTH_DATE)}</div>
              <div className="text-xs text-muted-foreground">Jason / Havilah</div>
            </div>
            <div>
              <div className="text-muted-foreground">Retirement Age</div>
              <div className="font-medium">{scenario.user_profile.retirement_age}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Annual Salary</div>
              <div className="font-medium">{formatCurrency(scenario.user_profile.annual_salary)}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Planning Years</div>
              <div className="font-medium">{projectionYears} years</div>
            </div>
          </div>
          
          {/* House Information Display */}
          {(() => {
            try {
              // Extract housing status from scenario name
              const isOwner = scenario.name.includes(' Own ')
              const isRenter = scenario.name.includes(' Rent ')
              
              console.log('Housing debug:', { 
                scenarioName: scenario.name, 
                isOwner, 
                isRenter,
                hasUserData: !!scenario.user_data 
              })
              
              const userData = JSON.parse(scenario.user_data || '{}')
              const expenses = userData.expenses || []
              
              // Find housing-related expenses
              const housingExpense = expenses.find((expense: any) => 
                expense.name?.toLowerCase().includes('housing')
              )
              const propertyTaxExpense = expenses.find((expense: any) => 
                expense.name?.toLowerCase().includes('property tax')
              )
              
              console.log('Expense debug:', { 
                expenseCount: expenses.length,
                housingExpense: housingExpense?.name,
                propertyTaxExpense: propertyTaxExpense?.name
              })
              
              if (isOwner || isRenter || housingExpense) {
                const monthlyRent = housingExpense?.line_items?.monthly_rent || 0
                const propertyTax = propertyTaxExpense?.annual_amount || (housingExpense?.line_items?.property_tax || 0) * 12
                const houseMaintenance = (housingExpense?.line_items?.house_maintenance || 0) * 12
                const hoaFees = (housingExpense?.line_items?.hoa_fees || 0) * 12
                
                let statusIcon = '🏠'
                let statusText = 'Housing'
                let bgColor = 'bg-blue-50 dark:bg-blue-950/20'
                let textColor = 'text-blue-900 dark:text-blue-100'
                let detailColor = 'text-blue-700 dark:text-blue-200'
                
                if (isOwner) {
                  statusIcon = '🏡'
                  statusText = 'Homeowner'
                  bgColor = 'bg-green-50 dark:bg-green-950/20'
                  textColor = 'text-green-900 dark:text-green-100'
                  detailColor = 'text-green-700 dark:text-green-200'
                } else if (isRenter) {
                  statusIcon = '🏢'
                  statusText = 'Renter'
                  bgColor = 'bg-orange-50 dark:bg-orange-950/20'
                  textColor = 'text-orange-900 dark:text-orange-100'
                  detailColor = 'text-orange-700 dark:text-orange-200'
                }
                
                return (
                  <div className={`mt-3 p-3 rounded-lg ${bgColor}`}>
                    <div className={`text-sm font-medium mb-1 ${textColor}`}>
                      {statusIcon} {statusText}
                    </div>
                    <div className={`text-xs space-y-1 ${detailColor}`}>
                      {isRenter && monthlyRent > 0 && (
                        <div><strong>Monthly Rent:</strong> {formatCurrency(monthlyRent)}</div>
                      )}
                      {isOwner && propertyTax > 0 && (
                        <div><strong>Property Tax:</strong> {formatCurrency(propertyTax)}/year</div>
                      )}
                      {isOwner && houseMaintenance > 0 && (
                        <div><strong>Maintenance:</strong> {formatCurrency(houseMaintenance)}/year</div>
                      )}
                      {hoaFees > 0 && (
                        <div><strong>HOA Fees:</strong> {formatCurrency(hoaFees)}/year</div>
                      )}
                      {housingExpense && (
                        <div><strong>Total Housing:</strong> {formatCurrency(housingExpense.annual_amount)}/year</div>
                      )}
                    </div>
                  </div>
                )
              }
            } catch (error) {
              console.log('Housing parsing error:', error)
            }
            return null
          })()}

          {scenario.scenario_type === 'retirement' && scenario.retirement_income_target && (
            <div className="p-3 bg-accent rounded-lg">
              <div className="text-sm text-muted-foreground">Retirement Income Target</div>
              <div className="font-semibold text-green-600">
                {formatCurrency(scenario.retirement_income_target)}/year
              </div>
            </div>
          )}

          {scenario.scenario_type === 'relocation' && scenario.relocation_city && (
            <div className="p-3 bg-accent rounded-lg">
              <div className="text-sm text-muted-foreground">Target City</div>
              <div className="font-semibold">{scenario.relocation_city}</div>
            </div>
          )}

          {scenario.scenario_type === 'major_purchase' && scenario.major_purchase_amount && (
            <div className="p-3 bg-accent rounded-lg">
              <div className="text-sm text-muted-foreground">Purchase Amount</div>
              <div className="font-semibold text-blue-600">
                {formatCurrency(scenario.major_purchase_amount)}
              </div>
            </div>
          )}

          <div className="flex space-x-2 pt-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="flex-1"
              onClick={(e) => {
                e.stopPropagation()
                onRunProjection?.(scenario)
              }}
            >
              <Play className="mr-1 h-3 w-3" />
              Project
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              className="flex-1"
              onClick={(e) => {
                e.stopPropagation()
                onRunMonteCarlo?.(scenario)
              }}
            >
              <BarChart3 className="mr-1 h-3 w-3" />
              Simulate
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function ScenarioList({ 
  onScenarioSelect, 
  onCreateNew, 
  onRunProjection, 
  onRunMonteCarlo 
}: ScenarioListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([])
  const { scenarios, isLoading, deleteScenario } = useScenarios()
  const { toast } = useToast()

  const filteredScenarios = scenarios.filter(scenario => {
    const matchesSearch = scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scenario.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || scenario.scenario_type === filterType
    return matchesSearch && matchesFilter
  })

  const handleDelete = (scenario: Scenario) => {
    if (window.confirm(`Are you sure you want to delete "${scenario.name}"?`)) {
      deleteScenario(scenario.id)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }, (_, i) => (
          <div key={i} className="h-64 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Financial Scenarios</h1>
          <p className="text-muted-foreground">
            Manage and analyze your financial planning scenarios
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={() => {
              const params = selectedForComparison.length > 0 
                ? `?scenarios=${selectedForComparison.join(',')}`
                : ''
              window.location.href = `/scenarios/compare${params}`
            }}
            className="flex items-center space-x-2"
            disabled={scenarios.length < 2}
          >
            <BarChart3 className="h-4 w-4" />
            <span>
              Compare Scenarios
              {selectedForComparison.length > 0 && ` (${selectedForComparison.length})`}
            </span>
          </Button>
          <Button onClick={onCreateNew} className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>Create Scenario</span>
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search scenarios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 border border-input rounded-md text-sm bg-background"
        >
          <option value="all">All Types</option>
          <option value="current">Current Plan</option>
          <option value="retirement">Early Retirement</option>
          <option value="relocation">City Relocation</option>
          <option value="education">Education Planning</option>
          <option value="major_purchase">Major Purchase</option>
        </select>
      </div>

      {/* Scenarios Grid */}
      {filteredScenarios.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            {scenarios.length === 0 ? (
              <>
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  No scenarios yet
                </h3>
                <p className="text-muted-foreground mb-6">
                  Create your first financial scenario to start planning your future.
                </p>
                <Button onClick={onCreateNew}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create First Scenario
                </Button>
              </>
            ) : (
              <>
                <Search className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  No scenarios found
                </h3>
                <p className="text-muted-foreground">
                  Try adjusting your search or filter criteria.
                </p>
              </>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredScenarios.map((scenario) => (
            <ScenarioCard
              key={scenario.id}
              scenario={scenario}
              onSelect={onScenarioSelect}
              onRunProjection={onRunProjection}
              onRunMonteCarlo={onRunMonteCarlo}
              onEdit={(scenario) => {
                toast({
                  title: "Edit Scenario",
                  description: "Scenario editing will be available soon.",
                  variant: "default"
                })
              }}
              onDelete={handleDelete}
              isSelectedForComparison={selectedForComparison.includes(scenario.id)}
              onComparisonToggle={(scenarioId, selected) => {
                if (selected) {
                  if (selectedForComparison.length < 4) {
                    setSelectedForComparison([...selectedForComparison, scenarioId])
                  } else {
                    toast({
                      title: "Selection Limit",
                      description: "You can only compare up to 4 scenarios at once.",
                      variant: "default"
                    })
                  }
                } else {
                  setSelectedForComparison(selectedForComparison.filter(id => id !== scenarioId))
                }
              }}
            />
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {scenarios.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Scenario Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-foreground">{scenarios.length}</div>
                <div className="text-sm text-muted-foreground">Total Scenarios</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {scenarios.filter(s => s.scenario_type === 'current').length}
                </div>
                <div className="text-sm text-muted-foreground">Current Plans</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {scenarios.filter(s => s.scenario_type === 'retirement').length}
                </div>
                <div className="text-sm text-muted-foreground">Retirement Plans</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">
                  {scenarios.filter(s => s.scenario_type === 'relocation').length}
                </div>
                <div className="text-sm text-muted-foreground">Relocation Plans</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ScenarioList