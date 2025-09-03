'use client'

import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  Circle, 
  ArrowLeft, 
  ArrowRight,
  User,
  DollarSign,
  Target,
  Settings
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/hooks/use-toast'
import { useScenarios } from '@/stores/app-store'
import apiClient from '@/lib/api'
import type { ScenarioFormData } from '@/types'

// Form validation schema
const scenarioSchema = z.object({
  // Basic Info
  name: z.string().min(1, 'Scenario name is required'),
  description: z.string().optional(),
  scenario_type: z.enum(['current', 'retirement', 'relocation', 'education', 'major_purchase']),
  
  // User Profile
  user_name: z.string().min(1, 'Name is required'),
  birth_date: z.string().min(1, 'Birth date is required'),
  current_age: z.number().min(18).max(100),
  retirement_age: z.number().min(50).max(80),
  life_expectancy: z.number().min(70).max(120),
  current_city: z.string().optional(),
  annual_salary: z.number().min(0),
  
  // Scenario-specific
  target_city: z.string().optional(),
  retirement_income_target: z.number().optional(),
  major_purchase_amount: z.number().optional(),
  
  // Assumptions
  inflation_rate: z.number().min(0).max(0.2),
  investment_return: z.number().min(0).max(0.5),
  salary_growth_rate: z.number().min(0).max(0.2),
  tax_rate: z.number().min(0).max(0.5),
})

type ScenarioFormValues = z.infer<typeof scenarioSchema>

const scenarioTypes = [
  { value: 'current', label: 'Current Financial Plan', description: 'Analyze your current financial trajectory' },
  { value: 'retirement', label: 'Early Retirement Analysis', description: 'Plan for early retirement scenarios' },
  { value: 'relocation', label: 'City Relocation Impact', description: 'Evaluate cost-of-living changes' },
  { value: 'education', label: 'Education Expenses Planning', description: 'Plan for education costs' },
  { value: 'major_purchase', label: 'Major Purchase Analysis', description: 'Analyze impact of large purchases' }
]

const steps = [
  { id: 1, title: 'Basic Info', icon: Circle, key: 'basic' },
  { id: 2, title: 'Profile', icon: User, key: 'profile' },
  { id: 3, title: 'Details', icon: Target, key: 'details' },
  { id: 4, title: 'Assumptions', icon: Settings, key: 'assumptions' }
]

interface StepIndicatorProps {
  currentStep: number
  steps: typeof steps
}

function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      {steps.map((step, index) => {
        const isActive = step.id === currentStep
        const isCompleted = step.id < currentStep
        const Icon = isCompleted ? CheckCircle : step.icon

        return (
          <div key={step.id} className="flex items-center">
            <div className={`flex items-center space-x-2 ${
              isActive ? 'text-primary' : isCompleted ? 'text-green-600' : 'text-muted-foreground'
            }`}>
              <Icon className="h-5 w-5" />
              <span className="text-sm font-medium">{step.title}</span>
            </div>
            {index < steps.length - 1 && (
              <div className={`w-12 h-0.5 mx-4 ${
                isCompleted ? 'bg-green-600' : 'bg-border'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

interface ScenarioBuilderProps {
  onScenarioCreated?: (scenarioId: string) => void
  onCancel?: () => void
}

export function ScenarioBuilder({ onScenarioCreated, onCancel }: ScenarioBuilderProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()
  const { addScenario } = useScenarios()

  const form = useForm<ScenarioFormValues>({
    resolver: zodResolver(scenarioSchema),
    defaultValues: {
      scenario_type: 'current',
      current_age: 35,
      retirement_age: 65,
      life_expectancy: 90,
      annual_salary: 75000,
      inflation_rate: 0.03,
      investment_return: 0.07,
      salary_growth_rate: 0.03,
      tax_rate: 0.22,
    }
  })

  const { control, handleSubmit, watch, formState: { errors } } = form
  const watchedScenarioType = watch('scenario_type')

  const onSubmit = async (data: ScenarioFormValues) => {
    setIsSubmitting(true)
    
    try {
      const scenarioData: ScenarioFormData = {
        name: data.name,
        description: data.description || '',
        scenario_type: data.scenario_type,
        user_profile: {
          name: data.user_name,
          birth_date: data.birth_date,
          current_age: data.current_age,
          retirement_age: data.retirement_age,
          life_expectancy: data.life_expectancy,
          current_city: data.current_city || '',
          annual_salary: data.annual_salary,
          assets: [],
          liabilities: [],
          income_sources: [],
          expenses: [],
          retirement_accounts: []
        },
        projection_settings: {
          projection_years: data.life_expectancy - data.current_age,
          assumptions: {
            inflation_rate: data.inflation_rate,
            investment_return: data.investment_return,
            salary_growth_rate: data.salary_growth_rate,
            tax_rate: data.tax_rate
          }
        },
        retirement_income_target: data.retirement_income_target,
        relocation_city: data.target_city,
        major_purchase_amount: data.major_purchase_amount
      }

      const scenarioId = await apiClient.createScenario(scenarioData)
      
      toast({
        title: "Scenario Created",
        description: `Successfully created "${data.name}" scenario.`,
        variant: "default"
      })

      if (onScenarioCreated) {
        onScenarioCreated(scenarioId)
      }
      
    } catch (error) {
      console.error('Failed to create scenario:', error)
      toast({
        title: "Error",
        description: "Failed to create scenario. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const nextStep = async () => {
    // Validate current step before proceeding
    const fieldsToValidate = getFieldsForStep(currentStep)
    const isValid = await form.trigger(fieldsToValidate)
    
    if (isValid && currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const previousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const getFieldsForStep = (step: number): (keyof ScenarioFormValues)[] => {
    switch (step) {
      case 1:
        return ['name', 'scenario_type']
      case 2:
        return ['user_name', 'birth_date', 'current_age', 'annual_salary']
      case 3:
        return watchedScenarioType === 'retirement' ? ['retirement_income_target'] :
               watchedScenarioType === 'relocation' ? ['target_city'] :
               watchedScenarioType === 'major_purchase' ? ['major_purchase_amount'] : []
      default:
        return []
    }
  }

  const renderBasicInfo = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <label className="text-sm font-medium text-foreground block mb-2">
          Scenario Name *
        </label>
        <Controller
          name="name"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              placeholder="e.g., Early Retirement Plan"
              className={errors.name ? 'border-destructive' : ''}
            />
          )}
        />
        {errors.name && (
          <p className="text-sm text-destructive mt-1">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label className="text-sm font-medium text-foreground block mb-2">
          Scenario Type *
        </label>
        <div className="grid gap-3">
          {scenarioTypes.map((type) => (
            <Controller
              key={type.value}
              name="scenario_type"
              control={control}
              render={({ field }) => (
                <label className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-accent transition-colors">
                  <input
                    type="radio"
                    {...field}
                    value={type.value}
                    checked={field.value === type.value}
                    className="mt-0.5"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{type.label}</div>
                    <div className="text-sm text-muted-foreground">{type.description}</div>
                  </div>
                </label>
              )}
            />
          ))}
        </div>
      </div>

      <div>
        <label className="text-sm font-medium text-foreground block mb-2">
          Description
        </label>
        <Controller
          name="description"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={3}
              placeholder="Describe what this scenario represents..."
              className="w-full px-3 py-2 border border-input rounded-md text-sm"
            />
          )}
        />
      </div>
    </motion.div>
  )

  const renderProfile = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Full Name *
          </label>
          <Controller
            name="user_name"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Your full name"
                className={errors.user_name ? 'border-destructive' : ''}
              />
            )}
          />
          {errors.user_name && (
            <p className="text-sm text-destructive mt-1">{errors.user_name.message}</p>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Birth Date *
          </label>
          <Controller
            name="birth_date"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="date"
                className={errors.birth_date ? 'border-destructive' : ''}
              />
            )}
          />
          {errors.birth_date && (
            <p className="text-sm text-destructive mt-1">{errors.birth_date.message}</p>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Current Age *
          </label>
          <Controller
            name="current_age"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="18"
                max="100"
                onChange={(e) => field.onChange(parseInt(e.target.value))}
                className={errors.current_age ? 'border-destructive' : ''}
              />
            )}
          />
          {errors.current_age && (
            <p className="text-sm text-destructive mt-1">{errors.current_age.message}</p>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Planned Retirement Age
          </label>
          <Controller
            name="retirement_age"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="50"
                max="80"
                onChange={(e) => field.onChange(parseInt(e.target.value))}
              />
            )}
          />
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Life Expectancy
          </label>
          <Controller
            name="life_expectancy"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="70"
                max="120"
                onChange={(e) => field.onChange(parseInt(e.target.value))}
              />
            )}
          />
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Annual Salary *
          </label>
          <Controller
            name="annual_salary"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="0"
                step="1000"
                placeholder="75000"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
                className={errors.annual_salary ? 'border-destructive' : ''}
              />
            )}
          />
          {errors.annual_salary && (
            <p className="text-sm text-destructive mt-1">{errors.annual_salary.message}</p>
          )}
        </div>
      </div>
    </motion.div>
  )

  const renderScenarioDetails = () => {
    if (watchedScenarioType === 'current') {
      return (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-center py-12"
        >
          <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Current Plan Analysis Ready
          </h3>
          <p className="text-muted-foreground">
            Your current financial plan is configured. Proceed to set assumptions.
          </p>
        </motion.div>
      )
    }

    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        className="space-y-6"
      >
        {watchedScenarioType === 'retirement' && (
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Target Retirement Income (Annual)
            </label>
            <Controller
              name="retirement_income_target"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="number"
                  min="0"
                  step="1000"
                  placeholder="60000"
                  onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                />
              )}
            />
            <p className="text-sm text-muted-foreground mt-1">
              Annual income needed in retirement (in today's dollars)
            </p>
          </div>
        )}

        {watchedScenarioType === 'relocation' && (
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Target City *
            </label>
            <Controller
              name="target_city"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  placeholder="e.g., San Francisco, CA"
                  className={errors.target_city ? 'border-destructive' : ''}
                />
              )}
            />
            {errors.target_city && (
              <p className="text-sm text-destructive mt-1">{errors.target_city.message}</p>
            )}
          </div>
        )}

        {watchedScenarioType === 'major_purchase' && (
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Purchase Amount *
            </label>
            <Controller
              name="major_purchase_amount"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="number"
                  min="0"
                  step="1000"
                  placeholder="50000"
                  onChange={(e) => field.onChange(parseFloat(e.target.value))}
                  className={errors.major_purchase_amount ? 'border-destructive' : ''}
                />
              )}
            />
            {errors.major_purchase_amount && (
              <p className="text-sm text-destructive mt-1">{errors.major_purchase_amount.message}</p>
            )}
          </div>
        )}
      </motion.div>
    )
  }

  const renderAssumptions = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Inflation Rate
          </label>
          <Controller
            name="inflation_rate"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="0"
                max="0.2"
                step="0.005"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
              />
            )}
          />
          <p className="text-sm text-muted-foreground mt-1">Annual inflation rate (3% = 0.03)</p>
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Investment Return
          </label>
          <Controller
            name="investment_return"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="0"
                max="0.5"
                step="0.005"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
              />
            )}
          />
          <p className="text-sm text-muted-foreground mt-1">Expected annual investment return (7% = 0.07)</p>
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Salary Growth Rate
          </label>
          <Controller
            name="salary_growth_rate"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="0"
                max="0.2"
                step="0.005"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
              />
            )}
          />
          <p className="text-sm text-muted-foreground mt-1">Annual salary increase rate</p>
        </div>

        <div>
          <label className="text-sm font-medium text-foreground block mb-2">
            Effective Tax Rate
          </label>
          <Controller
            name="tax_rate"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                type="number"
                min="0"
                max="0.5"
                step="0.01"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
              />
            )}
          />
          <p className="text-sm text-muted-foreground mt-1">Overall effective tax rate (22% = 0.22)</p>
        </div>
      </div>
    </motion.div>
  )

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderBasicInfo()
      case 2: return renderProfile()
      case 3: return renderScenarioDetails()
      case 4: return renderAssumptions()
      default: return renderBasicInfo()
    }
  }

  return (
    <div className="container mx-auto px-6 py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Create Financial Scenario</CardTitle>
              <CardDescription>
                Build a comprehensive financial planning scenario with personalized assumptions
              </CardDescription>
            </div>
            {onCancel && (
              <Button variant="outline" onClick={onCancel}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Cancel
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <StepIndicator currentStep={currentStep} steps={steps} />
            
            <div className="min-h-[400px]">
              {renderCurrentStep()}
            </div>

            <div className="flex justify-between pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={previousStep}
                disabled={currentStep === 1}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>

              {currentStep < steps.length ? (
                <Button type="button" onClick={nextStep}>
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create Scenario'}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}