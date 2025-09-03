'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useScenarios } from '@/hooks/use-scenarios'
import { 
  GraduationCap,
  Calculator,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  Users,
  School,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Info,
  Target
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency } from '@/lib/utils'

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

// Get financial data from scenario
const getFinancialDataFromScenario = (scenarioData: any) => {
  if (!scenarioData?.user_data) {
    // Fallback data with correct ages
    return {
      monthlyIncome: 0,
      monthlyExpenses: 23000,
      monthlySurplus: -23000,
      liquidSavings: 100000,
      investments: 4790000,
      havilahAge: userData.havilah_age || calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: userData.jason_age || calculateAge(JASON_BIRTH_DATE),
      emergencyFundMonths: 6
    }
  }

  try {
    const userData = JSON.parse(scenarioData.user_data)
    const totalAssets = userData.assets?.filter((asset: any) => 
      !asset.name?.toLowerCase().includes('principal') && 
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
    const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
    const monthlyExpenses = totalExpenses / 12
    const monthlyIncome = (userData.annual_salary || 0) / 12
    const monthlySurplus = monthlyIncome - monthlyExpenses
    
    // Separate retirement vs non-retirement assets (exclude summary accounts)
    const retirementAssets = userData.assets?.filter((asset: any) => 
      (asset.name?.includes('401') || 
       asset.name?.includes('IRA') || 
       asset.name?.includes('Roth')) &&
      !asset.name?.toLowerCase().includes('principal') && // Exclude summary accounts
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
    
    // Liquid assets estimation (conservative)
    const liquidAssets = userData.assets?.filter((asset: any) => 
      asset.name?.toLowerCase().includes('savings') || 
      asset.name?.toLowerCase().includes('cash') ||
      asset.name?.toLowerCase().includes('checking')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || Math.min(200000, totalAssets * 0.05)
    
    // Non-retirement investments
    const nonRetirementAssets = totalAssets - retirementAssets
    const investments = Math.max(0, nonRetirementAssets - liquidAssets)
    
    return {
      monthlyIncome,
      monthlyExpenses,
      monthlySurplus,
      liquidSavings: liquidAssets,
      investments: investments,
      havilahAge: userData.havilah_age || calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: userData.jason_age || calculateAge(JASON_BIRTH_DATE),
      emergencyFundMonths: 6
    }
  } catch (error) {
    console.error('Error parsing scenario data for private school:', error)
    return {
      monthlyIncome: 0,
      monthlyExpenses: 23000,
      monthlySurplus: -23000,
      liquidSavings: 100000,
      investments: 4790000,
      havilahAge: userData.havilah_age || calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: userData.jason_age || calculateAge(JASON_BIRTH_DATE),
      emergencyFundMonths: 6
    }
  }
}

// Child data structure
interface Child {
  id: string
  name: string
  currentAge: number
  currentGrade: number
  startPrivateGrade?: number
  endPrivateGrade?: number
}

// School cost scenarios
interface SchoolScenario {
  name: string
  annualCost: number
  description: string
  includes: string[]
}

const schoolScenarios: SchoolScenario[] = [
  {
    name: "Premium Private School",
    annualCost: 65000,
    description: "Top-tier private school with extensive programs",
    includes: ["Tuition", "Technology fees", "Athletics", "Arts programs", "College counseling"]
  },
  {
    name: "Standard Private School", 
    annualCost: 45000,
    description: "Quality private education with good academics",
    includes: ["Tuition", "Basic technology", "Some activities", "College prep"]
  },
  {
    name: "Religious Private School",
    annualCost: 35000,
    description: "Faith-based education with strong values",
    includes: ["Tuition", "Religious studies", "Basic activities", "Community service"]
  }
]

function ChildTimeline({ child, schoolScenario, onUpdate }: { 
  child: Child, 
  schoolScenario: SchoolScenario,
  onUpdate: (child: Child) => void 
}) {
  const [editedChild, setEditedChild] = useState(child)
  
  const grades = Array.from({ length: 13 }, (_, i) => ({ 
    grade: i, 
    label: i === 0 ? 'K' : i.toString(),
    age: child.currentAge - child.currentGrade + i
  }))
  
  const calculateCosts = () => {
    if (!editedChild.startPrivateGrade || !editedChild.endPrivateGrade) return { totalCost: 0, years: 0 }
    
    const years = editedChild.endPrivateGrade - editedChild.startPrivateGrade + 1
    const totalCost = years * schoolScenario.annualCost
    
    return { totalCost, years }
  }
  
  const { totalCost, years } = calculateCosts()
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Users className="h-5 w-5 mr-2" />
          {editedChild.name}
        </CardTitle>
        <CardDescription>
          Currently {editedChild.currentAge} years old, Grade {editedChild.currentGrade === 0 ? 'K' : editedChild.currentGrade}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Grade Timeline */}
          <div>
            <div className="text-sm font-medium mb-2">Private School Timeline</div>
            <div className="grid grid-cols-6 md:grid-cols-13 gap-1">
              {grades.map((gradeData) => {
                const isPrivate = editedChild.startPrivateGrade !== undefined && 
                                editedChild.endPrivateGrade !== undefined &&
                                gradeData.grade >= editedChild.startPrivateGrade && 
                                gradeData.grade <= editedChild.endPrivateGrade
                const isCurrent = gradeData.grade === editedChild.currentGrade
                const isPast = gradeData.grade < editedChild.currentGrade
                
                return (
                  <div key={gradeData.grade} className="text-center">
                    <div 
                      className={`h-8 w-8 rounded text-xs flex items-center justify-center cursor-pointer border-2 transition-colors ${
                        isPast 
                          ? 'bg-gray-300 text-gray-600 border-gray-400' 
                          : isCurrent 
                          ? 'bg-blue-500 text-white border-blue-600' 
                          : isPrivate 
                          ? 'bg-green-500 text-white border-green-600' 
                          : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'
                      }`}
                      onClick={() => {
                        if (!isPast) {
                          if (editedChild.startPrivateGrade === gradeData.grade) {
                            setEditedChild({ ...editedChild, startPrivateGrade: undefined })
                          } else if (!editedChild.startPrivateGrade || gradeData.grade < editedChild.startPrivateGrade) {
                            setEditedChild({ ...editedChild, startPrivateGrade: gradeData.grade })
                          } else if (!editedChild.endPrivateGrade || gradeData.grade > (editedChild.endPrivateGrade || 0)) {
                            setEditedChild({ ...editedChild, endPrivateGrade: gradeData.grade })
                          } else {
                            setEditedChild({ ...editedChild, endPrivateGrade: gradeData.grade })
                          }
                        }
                      }}
                    >
                      {gradeData.label}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Age {gradeData.age}
                    </div>
                  </div>
                )
              })}
            </div>
            <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-2">
              <div className="flex items-center">
                <div className="h-3 w-3 bg-gray-300 rounded mr-1"></div>
                Past
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-blue-500 rounded mr-1"></div>
                Current
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-green-500 rounded mr-1"></div>
                Private School
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-white border border-gray-300 rounded mr-1"></div>
                Public School
              </div>
            </div>
          </div>
          
          {/* Cost Summary */}
          {years > 0 && (
            <div className="bg-muted p-4 rounded-lg">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Duration</div>
                  <div className="font-semibold">{years} years</div>
                  <div className="text-xs text-muted-foreground">
                    Grades {editedChild.startPrivateGrade === 0 ? 'K' : editedChild.startPrivateGrade} - {editedChild.endPrivateGrade}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total Cost</div>
                  <div className="font-semibold text-lg text-primary">{formatCurrency(totalCost)}</div>
                  <div className="text-xs text-muted-foreground">
                    {formatCurrency(schoolScenario.annualCost)}/year
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <Button 
            onClick={() => onUpdate(editedChild)}
            className="w-full"
            disabled={!editedChild.startPrivateGrade || !editedChild.endPrivateGrade}
          >
            Update Timeline
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function CashFlowImpact({ children, schoolScenario, currentFinancials }: { children: Child[], schoolScenario: SchoolScenario, currentFinancials: any }) {
  // Calculate year-by-year costs
  const calculateYearlyImpact = () => {
    const currentYear = new Date().getFullYear()
    const yearlyData = []
    
    for (let year = 0; year < 12; year++) {
      const targetYear = currentYear + year
      let totalSchoolCost = 0
      
      children.forEach(child => {
        if (child.startPrivateGrade !== undefined && child.endPrivateGrade !== undefined) {
          const childGradeInYear = child.currentGrade + year
          if (childGradeInYear >= child.startPrivateGrade && childGradeInYear <= child.endPrivateGrade) {
            totalSchoolCost += schoolScenario.annualCost
          }
        }
      })
      
      const monthlySchoolCost = totalSchoolCost / 12
      const remainingSurplus = currentFinancials.monthlySurplus - monthlySchoolCost
      const cumulativeSavings = currentFinancials.liquidSavings + (remainingSurplus * 12 * (year + 1))
      
      yearlyData.push({
        year: targetYear,
        yearOffset: year,
        annualSchoolCost: totalSchoolCost,
        monthlySchoolCost,
        remainingSurplus,
        cumulativeSavings: Math.max(0, cumulativeSavings),
        isAffordable: remainingSurplus > 0 && cumulativeSavings > 0
      })
    }
    
    return yearlyData
  }
  
  const yearlyData = calculateYearlyImpact()
  const totalPrivateSchoolCost = children.reduce((total, child) => {
    if (child.startPrivateGrade !== undefined && child.endPrivateGrade !== undefined) {
      const years = child.endPrivateGrade - child.startPrivateGrade + 1
      return total + (years * schoolScenario.annualCost)
    }
    return total
  }, 0)
  
  const peakYearCost = Math.max(...yearlyData.map(d => d.annualSchoolCost))
  const peakYearData = yearlyData.find(d => d.annualSchoolCost === peakYearCost)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Cash Flow Impact Analysis
        </CardTitle>
        <CardDescription>
          How private school costs will affect your finances over time
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(totalPrivateSchoolCost)}
              </div>
              <div className="text-sm text-muted-foreground">Total Cost</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(peakYearCost)}
              </div>
              <div className="text-sm text-muted-foreground">Peak Year Cost</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${peakYearData?.remainingSurplus ? (peakYearData.remainingSurplus > 0 ? 'text-green-600' : 'text-red-600') : 'text-gray-600'}`}>
                {peakYearData ? formatCurrency(peakYearData.remainingSurplus) : 'N/A'}
              </div>
              <div className="text-sm text-muted-foreground">Peak Year Surplus</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {yearlyData.filter(d => d.annualSchoolCost > 0).length}
              </div>
              <div className="text-sm text-muted-foreground">Years Paying</div>
            </div>
          </div>
          
          {/* Year by Year Breakdown */}
          <div>
            <h4 className="font-semibold mb-3">Year-by-Year Impact</h4>
            <div className="space-y-2">
              {yearlyData.filter(d => d.annualSchoolCost > 0).map((data) => (
                <div key={data.year} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-sm font-medium">{data.year}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatCurrency(data.annualSchoolCost)}/year
                    </div>
                    {!data.isAffordable && (
                      <Badge variant="destructive" className="text-xs">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Cash Flow Risk
                      </Badge>
                    )}
                  </div>
                  <div className="text-right">
                    <div className={`font-semibold ${data.remainingSurplus > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(data.remainingSurplus)}/month surplus
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatCurrency(data.cumulativeSavings)} savings
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Affordability Assessment */}
          <div className="p-4 border rounded-lg">
            {peakYearData?.remainingSurplus && peakYearData.remainingSurplus > 0 ? (
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <div className="font-semibold text-green-600">Financially Feasible</div>
                  <div className="text-sm text-muted-foreground">
                    You can afford this private school plan while maintaining positive cash flow. 
                    Even in the peak cost year ({peakYearData.year}), you'll have {formatCurrency(peakYearData.remainingSurplus)} monthly surplus.
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <div className="font-semibold text-red-600">Cash Flow Concerns</div>
                  <div className="text-sm text-muted-foreground">
                    This plan would create negative cash flow in {peakYearData?.year}. 
                    Consider adjusting the timeline, choosing a less expensive school, or increasing income.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function PrivateSchoolAnalysis() {
  const router = useRouter()
  const [selectedScenario, setSelectedScenario] = useState(schoolScenarios[0])
  const [selectedFinancialScenario, setSelectedFinancialScenario] = useState<any>(null)
  const [currentFinancials, setCurrentFinancials] = useState<any>(null)
  const [children, setChildren] = useState<Child[]>([
    { id: '1', name: 'Tate', currentAge: 15, currentGrade: 9, startPrivateGrade: 9, endPrivateGrade: 12 },
    { id: '2', name: 'Wynn', currentAge: 13, currentGrade: 7, startPrivateGrade: 9, endPrivateGrade: 12 }
  ])
  
  const { scenarios, isLoading } = useScenarios()

  // Load financial data from scenarios
  useEffect(() => {
    if (scenarios.length > 0 && !selectedFinancialScenario) {
      // Find the best scenario for financial data
      let defaultScenario = scenarios.find(scenario => 
        scenario.name.toLowerCase().includes('8yrs') && 
        scenario.name.toLowerCase().includes('work work')
      )
      
      if (!defaultScenario) {
        defaultScenario = scenarios.find(scenario => 
          scenario.name.toLowerCase().includes('8yrs')
        )
      }
      
      if (!defaultScenario) {
        defaultScenario = scenarios[0]
      }
      
      if (defaultScenario) {
        // Fetch full scenario data
        fetch(`http://localhost:8000/api/scenarios/${defaultScenario.id}`)
          .then(res => res.json())
          .then(fullScenario => {
            setSelectedFinancialScenario(fullScenario)
            const financialData = getFinancialDataFromScenario(fullScenario)
            setCurrentFinancials(financialData)
          })
          .catch(err => {
            console.error('Failed to load scenario for private school:', err)
            const fallbackData = getFinancialDataFromScenario(null)
            setCurrentFinancials(fallbackData)
          })
      }
    }
  }, [scenarios, selectedFinancialScenario])

  // Use fallback data if still loading
  const financials = currentFinancials || getFinancialDataFromScenario(null)
  
  const updateChild = (updatedChild: Child) => {
    setChildren(prev => prev.map(child => 
      child.id === updatedChild.id ? updatedChild : child
    ))
  }
  
  const addChild = () => {
    const newChild: Child = {
      id: Date.now().toString(),
      name: `Child ${children.length + 1}`,
      currentAge: 10,
      currentGrade: 4
    }
    setChildren(prev => [...prev, newChild])
  }
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Private School Cost Analysis
              </h1>
              <p className="text-muted-foreground mt-1">
                Plan and budget for private school education costs
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button 
                variant="outline"
                onClick={() => router.push('/forecasting')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Forecasting
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <Tabs defaultValue="planner" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="planner">School Timeline Planner</TabsTrigger>
            <TabsTrigger value="impact">Cash Flow Impact</TabsTrigger>
            <TabsTrigger value="alternatives">Alternatives & Strategies</TabsTrigger>
          </TabsList>
          
          <TabsContent value="planner" className="space-y-6">
            {/* School Scenario Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <School className="h-5 w-5 mr-2" />
                  School Cost Scenarios
                </CardTitle>
                <CardDescription>
                  Choose a school type to analyze costs and affordability
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-foreground">Current Ages</h4>
                      <p className="text-sm text-muted-foreground">Updated birth dates reflected</p>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-center">
                        <div className="text-xl font-bold text-primary">{financials.jasonAge}</div>
                        <div className="text-xs text-muted-foreground">Jason</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-primary">{financials.havilahAge}</div>
                        <div className="text-xs text-muted-foreground">Havilah</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="grid gap-4 md:grid-cols-3">
                  {schoolScenarios.map((scenario) => (
                    <Card 
                      key={scenario.name}
                      className={`cursor-pointer transition-colors ${
                        selectedScenario.name === scenario.name 
                          ? 'ring-2 ring-primary bg-primary/5' 
                          : 'hover:bg-muted/50'
                      }`}
                      onClick={() => setSelectedScenario(scenario)}
                    >
                      <CardHeader>
                        <CardTitle className="text-lg">{scenario.name}</CardTitle>
                        <div className="text-2xl font-bold text-primary">
                          {formatCurrency(scenario.annualCost)}/year
                        </div>
                        <CardDescription>{scenario.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-1">
                          {scenario.includes.map((item, index) => (
                            <div key={index} className="text-sm flex items-center">
                              <CheckCircle className="h-3 w-3 text-green-600 mr-2" />
                              {item}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            {/* Children Timeline */}
            <div className="grid gap-6 lg:grid-cols-2">
              {children.map((child) => (
                <ChildTimeline
                  key={child.id}
                  child={child}
                  schoolScenario={selectedScenario}
                  onUpdate={updateChild}
                />
              ))}
            </div>
            
            <Card>
              <CardContent className="pt-6">
                <Button onClick={addChild} variant="outline" className="w-full">
                  <Users className="h-4 w-4 mr-2" />
                  Add Another Child
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="impact">
            <CashFlowImpact children={children} schoolScenario={selectedScenario} currentFinancials={financials} />
          </TabsContent>
          
          <TabsContent value="alternatives">
            <Card>
              <CardHeader>
                <CardTitle>Alternatives & Strategies</CardTitle>
                <CardDescription>
                  Ways to make private school more affordable or explore other options
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <h4 className="font-semibold mb-3">Cost Reduction Strategies</h4>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <Target className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                          <div className="font-medium">Financial Aid & Scholarships</div>
                          <div className="text-sm text-muted-foreground">
                            Many private schools offer need-based aid. Could reduce costs by 20-40%.
                          </div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Target className="h-5 w-5 text-green-600 mt-0.5" />
                        <div>
                          <div className="font-medium">Payment Plans</div>
                          <div className="text-sm text-muted-foreground">
                            Monthly payment plans can help with cash flow management.
                          </div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Target className="h-5 w-5 text-purple-600 mt-0.5" />
                        <div>
                          <div className="font-medium">Tax Benefits</div>
                          <div className="text-sm text-muted-foreground">
                            529 plans and education credits can provide tax advantages.
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-3">Alternative Options</h4>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <Info className="h-5 w-5 text-orange-600 mt-0.5" />
                        <div>
                          <div className="font-medium">High-Quality Public Schools</div>
                          <div className="text-sm text-muted-foreground">
                            Research top-rated public schools in your area or consider moving.
                          </div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Info className="h-5 w-5 text-cyan-600 mt-0.5" />
                        <div>
                          <div className="font-medium">Charter/Magnet Schools</div>
                          <div className="text-sm text-muted-foreground">
                            Free public alternatives with specialized programs.
                          </div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Info className="h-5 w-5 text-indigo-600 mt-0.5" />
                        <div>
                          <div className="font-medium">Homeschooling</div>
                          <div className="text-sm text-muted-foreground">
                            Lower cost option with complete curriculum control.
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}