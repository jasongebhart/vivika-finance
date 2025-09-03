// Financial health scoring system based on dynamic scenario results

export interface FinancialHealthMetrics {
  // Core financial metrics
  netWorth: number
  monthlyIncome: number
  monthlyExpenses: number
  monthlySurplus: number
  liquidSavings: number
  investments: number
  annualGrowthRate: number
  
  // Demographic data
  currentAge: number
  projectionYears: number
  
  // Scenario results
  projectedNetWorth?: number
  retirementReadiness?: boolean
  
  // Dynamic scenario specific
  location?: string
  housingType?: string
  schoolType?: string
}

export interface HealthScore {
  overall: number // 0-100
  category: 'excellent' | 'good' | 'fair' | 'needs_improvement' | 'critical'
  color: string
  description: string
  breakdown: {
    cashFlow: { score: number; weight: number; description: string }
    netWorth: { score: number; weight: number; description: string }
    emergencyFund: { score: number; weight: number; description: string }
    growthRate: { score: number; weight: number; description: string }
    retirementReadiness: { score: number; weight: number; description: string }
    debtToIncome: { score: number; weight: number; description: string }
  }
  recommendations: string[]
  strengths: string[]
  concerns: string[]
}

const SCORING_WEIGHTS = {
  cashFlow: 0.25,        // 25% - Monthly surplus as % of income
  netWorth: 0.20,        // 20% - Net worth relative to age and income
  emergencyFund: 0.15,   // 15% - Liquid savings coverage
  growthRate: 0.15,      // 15% - Investment growth performance
  retirementReadiness: 0.15, // 15% - On track for retirement
  debtToIncome: 0.10     // 10% - Debt service ratio
}

export function calculateFinancialHealthScore(metrics: FinancialHealthMetrics): HealthScore {
  const scores = {
    cashFlow: calculateCashFlowScore(metrics),
    netWorth: calculateNetWorthScore(metrics),
    emergencyFund: calculateEmergencyFundScore(metrics),
    growthRate: calculateGrowthRateScore(metrics),
    retirementReadiness: calculateRetirementReadinessScore(metrics),
    debtToIncome: calculateDebtToIncomeScore(metrics)
  }
  
  // Calculate weighted overall score
  const overall = Math.round(
    scores.cashFlow.score * SCORING_WEIGHTS.cashFlow +
    scores.netWorth.score * SCORING_WEIGHTS.netWorth +
    scores.emergencyFund.score * SCORING_WEIGHTS.emergencyFund +
    scores.growthRate.score * SCORING_WEIGHTS.growthRate +
    scores.retirementReadiness.score * SCORING_WEIGHTS.retirementReadiness +
    scores.debtToIncome.score * SCORING_WEIGHTS.debtToIncome
  )
  
  const category = getScoreCategory(overall)
  const { color, description } = getCategoryInfo(category)
  
  return {
    overall,
    category,
    color,
    description,
    breakdown: {
      cashFlow: { ...scores.cashFlow, weight: SCORING_WEIGHTS.cashFlow },
      netWorth: { ...scores.netWorth, weight: SCORING_WEIGHTS.netWorth },
      emergencyFund: { ...scores.emergencyFund, weight: SCORING_WEIGHTS.emergencyFund },
      growthRate: { ...scores.growthRate, weight: SCORING_WEIGHTS.growthRate },
      retirementReadiness: { ...scores.retirementReadiness, weight: SCORING_WEIGHTS.retirementReadiness },
      debtToIncome: { ...scores.debtToIncome, weight: SCORING_WEIGHTS.debtToIncome }
    },
    recommendations: generateRecommendations(scores, metrics),
    strengths: generateStrengths(scores),
    concerns: generateConcerns(scores)
  }
}

function calculateCashFlowScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  const surplusRatio = metrics.monthlySurplus / metrics.monthlyIncome
  
  let score: number
  let description: string
  
  if (surplusRatio >= 0.20) {
    score = 100
    description = "Excellent cash flow with 20%+ monthly surplus"
  } else if (surplusRatio >= 0.15) {
    score = 85
    description = "Strong cash flow with healthy monthly surplus"
  } else if (surplusRatio >= 0.10) {
    score = 70
    description = "Good cash flow with adequate surplus"
  } else if (surplusRatio >= 0.05) {
    score = 55
    description = "Fair cash flow but limited surplus"
  } else if (surplusRatio > 0) {
    score = 35
    description = "Tight cash flow with minimal surplus"
  } else {
    score = 10
    description = "Negative cash flow - expenses exceed income"
  }
  
  return { score, description }
}

function calculateNetWorthScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  // Age-based net worth benchmarks (conservative estimates)
  const ageMultiplier = Math.max(1, metrics.currentAge - 22) // Working years
  const expectedNetWorth = metrics.monthlyIncome * 12 * ageMultiplier * 0.3 // 30% of cumulative income
  
  const netWorthRatio = metrics.netWorth / Math.max(expectedNetWorth, 50000) // Min $50k baseline
  
  let score: number
  let description: string
  
  if (netWorthRatio >= 2.0) {
    score = 100
    description = "Exceptional net worth - well above age benchmarks"
  } else if (netWorthRatio >= 1.5) {
    score = 85
    description = "Strong net worth relative to age and income"
  } else if (netWorthRatio >= 1.0) {
    score = 70
    description = "Good net worth on track with benchmarks"
  } else if (netWorthRatio >= 0.7) {
    score = 55
    description = "Fair net worth but below age benchmarks"
  } else if (netWorthRatio >= 0.4) {
    score = 35
    description = "Below average net worth for age group"
  } else {
    score = 15
    description = "Significantly below net worth benchmarks"
  }
  
  return { score, description }
}

function calculateEmergencyFundScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  const monthsCovered = metrics.liquidSavings / metrics.monthlyExpenses
  
  let score: number
  let description: string
  
  if (monthsCovered >= 12) {
    score = 100
    description = "Excellent emergency fund - 12+ months of expenses"
  } else if (monthsCovered >= 8) {
    score = 90
    description = "Strong emergency fund - 8+ months covered"
  } else if (monthsCovered >= 6) {
    score = 80
    description = "Good emergency fund - 6+ months covered"
  } else if (monthsCovered >= 3) {
    score = 60
    description = "Adequate emergency fund - 3+ months covered"
  } else if (monthsCovered >= 1) {
    score = 30
    description = "Minimal emergency fund - less than 3 months"
  } else {
    score = 5
    description = "No emergency fund - significant financial risk"
  }
  
  return { score, description }
}

function calculateGrowthRateScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  const growthRate = metrics.annualGrowthRate || 0.07
  
  let score: number
  let description: string
  
  if (growthRate >= 0.12) {
    score = 100
    description = "Exceptional investment growth rate"
  } else if (growthRate >= 0.10) {
    score = 85
    description = "Strong investment performance"  
  } else if (growthRate >= 0.08) {
    score = 75
    description = "Good investment growth above market average"
  } else if (growthRate >= 0.06) {
    score = 60
    description = "Fair investment growth near market average"
  } else if (growthRate >= 0.04) {
    score = 40
    description = "Below average investment performance"
  } else {
    score = 20
    description = "Poor investment growth - review strategy"
  }
  
  return { score, description }
}

function calculateRetirementReadinessScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  const yearsToRetirement = 65 - metrics.currentAge
  
  // Simple retirement readiness calculation
  const projectedWealth = metrics.projectedNetWorth || 
    (metrics.netWorth * Math.pow(1 + metrics.annualGrowthRate, yearsToRetirement))
  
  const retirementTarget = metrics.monthlyExpenses * 12 * 25 // 25x annual expenses rule
  const readinessRatio = projectedWealth / retirementTarget
  
  let score: number
  let description: string
  
  if (metrics.retirementReadiness === true || readinessRatio >= 1.2) {
    score = 100
    description = "Excellent retirement readiness - on track or ahead"
  } else if (readinessRatio >= 1.0) {
    score = 85
    description = "Good retirement readiness - meeting targets"
  } else if (readinessRatio >= 0.8) {
    score = 70
    description = "Fair retirement readiness - mostly on track"
  } else if (readinessRatio >= 0.6) {
    score = 50
    description = "Below retirement targets - increase savings"
  } else if (readinessRatio >= 0.4) {
    score = 30
    description = "Significantly behind retirement goals"
  } else {
    score = 10
    description = "Critical retirement shortfall - urgent action needed"
  }
  
  return { score, description }
}

function calculateDebtToIncomeScore(metrics: FinancialHealthMetrics): { score: number; description: string } {
  // Estimate debt service from expense minus surplus
  const discretionaryExpenses = metrics.monthlyExpenses - metrics.monthlySurplus
  const estimatedDebtService = Math.max(0, discretionaryExpenses * 0.3) // Assume 30% of discretionary is debt
  const debtToIncomeRatio = estimatedDebtService / metrics.monthlyIncome
  
  let score: number
  let description: string
  
  if (debtToIncomeRatio <= 0.10) {
    score = 100
    description = "Minimal debt burden - excellent financial flexibility"
  } else if (debtToIncomeRatio <= 0.20) {
    score = 85
    description = "Low debt burden - good financial position"
  } else if (debtToIncomeRatio <= 0.30) {
    score = 70
    description = "Moderate debt burden - manageable levels"
  } else if (debtToIncomeRatio <= 0.40) {
    score = 50
    description = "High debt burden - limiting financial flexibility"
  } else if (debtToIncomeRatio <= 0.50) {
    score = 25
    description = "Very high debt burden - significant concern"
  } else {
    score = 5
    description = "Critical debt burden - urgent debt reduction needed"
  }
  
  return { score, description }
}

function getScoreCategory(score: number): HealthScore['category'] {
  if (score >= 85) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 55) return 'fair'
  if (score >= 40) return 'needs_improvement'
  return 'critical'
}

function getCategoryInfo(category: HealthScore['category']): { color: string; description: string } {
  switch (category) {
    case 'excellent':
      return {
        color: 'text-green-600',
        description: 'Outstanding financial health with strong fundamentals across all areas'
      }
    case 'good':
      return {
        color: 'text-blue-600',
        description: 'Strong financial health with most metrics performing well'
      }
    case 'fair':
      return {
        color: 'text-yellow-600',
        description: 'Decent financial health with some areas for improvement'
      }
    case 'needs_improvement':
      return {
        color: 'text-orange-600',
        description: 'Financial health needs attention in several key areas'
      }
    case 'critical':
      return {
        color: 'text-red-600',
        description: 'Financial health requires immediate attention and action'
      }
  }
}

function generateRecommendations(
  scores: Record<string, { score: number; description: string }>,
  metrics: FinancialHealthMetrics
): string[] {
  const recommendations: string[] = []
  
  // Cash flow recommendations
  if (scores.cashFlow.score < 60) {
    if (metrics.monthlySurplus < 0) {
      recommendations.push("Immediate action: Reduce monthly expenses or increase income to achieve positive cash flow")
    } else {
      recommendations.push("Increase monthly surplus by optimizing expenses or boosting income")
    }
  }
  
  // Emergency fund recommendations
  if (scores.emergencyFund.score < 60) {
    recommendations.push("Build emergency fund to cover 3-6 months of expenses")
  }
  
  // Net worth recommendations
  if (scores.netWorth.score < 60) {
    recommendations.push("Focus on increasing net worth through consistent saving and investing")
  }
  
  // Growth rate recommendations
  if (scores.growthRate.score < 60) {
    recommendations.push("Review investment strategy to improve portfolio performance")
  }
  
  // Retirement recommendations
  if (scores.retirementReadiness.score < 60) {
    recommendations.push("Increase retirement contributions and consider more aggressive savings strategy")
  }
  
  // Debt recommendations
  if (scores.debtToIncome.score < 60) {
    recommendations.push("Develop debt reduction strategy to improve financial flexibility")
  }
  
  return recommendations.slice(0, 4) // Limit to top 4 recommendations
}

function generateStrengths(
  scores: Record<string, { score: number; description: string }>
): string[] {
  const strengths: string[] = []
  
  Object.entries(scores).forEach(([key, value]) => {
    if (value.score >= 80) {
      switch (key) {
        case 'cashFlow':
          strengths.push("Strong monthly cash flow and surplus")
          break
        case 'netWorth':
          strengths.push("Excellent net worth accumulation")
          break
        case 'emergencyFund':
          strengths.push("Well-funded emergency reserves")
          break
        case 'growthRate':
          strengths.push("Strong investment performance")
          break
        case 'retirementReadiness':
          strengths.push("On track for comfortable retirement")
          break
        case 'debtToIncome':
          strengths.push("Low debt burden and financial flexibility")
          break
      }
    }
  })
  
  return strengths
}

function generateConcerns(
  scores: Record<string, { score: number; description: string }>
): string[] {
  const concerns: string[] = []
  
  Object.entries(scores).forEach(([key, value]) => {
    if (value.score < 50) {
      switch (key) {
        case 'cashFlow':
          concerns.push("Limited or negative monthly cash flow")
          break
        case 'netWorth':
          concerns.push("Net worth below age-appropriate benchmarks")
          break
        case 'emergencyFund':
          concerns.push("Insufficient emergency fund coverage")
          break
        case 'growthRate':
          concerns.push("Below-average investment returns")
          break
        case 'retirementReadiness':
          concerns.push("Behind on retirement savings goals")
          break
        case 'debtToIncome':
          concerns.push("High debt burden limiting flexibility")
          break
      }
    }
  })
  
  return concerns
}