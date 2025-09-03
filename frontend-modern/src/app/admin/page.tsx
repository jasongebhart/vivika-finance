'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Home, 
  DollarSign, 
  Receipt, 
  Download, 
  Upload,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  ArrowLeft
} from 'lucide-react'
import { useRouter } from 'next/navigation'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { getAPIUrl, API_CONFIG } from '@/lib/config'

// Simple Label component since it's not in the UI library
const Label = ({ htmlFor, children, ...props }: { htmlFor?: string, children: React.ReactNode, className?: string }) => (
  <label htmlFor={htmlFor} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" {...props}>
    {children}
  </label>
)

interface HouseData {
  description: string
  cost_basis: number
  closing_costs: number
  home_improvement: number
  value: number
  mortgage_principal: number
  commission_rate: number
  annual_growth_rate: number
  interest_rate: number
  monthly_payment: number
  payments_made: number
  number_of_payments: number
  annual_property_tax: number
  sell_house: boolean
}

interface TaxRates {
  assumed: number
  federal_single: number
  state_single: number
  federal_dual: number
  state_dual: number
}

export default function AdminPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [houseData, setHouseData] = useState<{ house: HouseData, new_house: HouseData } | null>(null)
  const [taxRates, setTaxRates] = useState<TaxRates | null>(null)
  const [originalHouseData, setOriginalHouseData] = useState<any>(null)
  const [originalTaxRates, setOriginalTaxRates] = useState<any>(null)

  useEffect(() => {
    loadConfiguration()
  }, [])

  const loadConfiguration = async () => {
    setIsLoading(true)
    try {
      // Load house data using proper API configuration
      const houseUrl = getAPIUrl(API_CONFIG.endpoints.houseData)
      const houseResponse = await fetch(houseUrl)
      if (houseResponse.ok) {
        const houses = await houseResponse.json()
        setHouseData(houses)
        setOriginalHouseData(JSON.parse(JSON.stringify(houses)))
      } else {
        throw new Error(`House data API failed: ${houseResponse.status}`)
      }

      // Load full config to get tax rates
      const configUrl = getAPIUrl(API_CONFIG.endpoints.financialConfig)
      const configResponse = await fetch(configUrl)
      if (configResponse.ok) {
        const config = await configResponse.json()
        if (config.TAX_RATES) {
          setTaxRates(config.TAX_RATES)
          setOriginalTaxRates(JSON.parse(JSON.stringify(config.TAX_RATES)))
        }
      } else {
        throw new Error(`Config API failed: ${configResponse.status}`)
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Failed to load configuration: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  const updateHouseData = async () => {
    if (!houseData) return

    setIsLoading(true)
    try {
      const apiUrl = getAPIUrl(API_CONFIG.endpoints.adminHouseData)
      const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(houseData)
      })

      if (response.ok) {
        const result = await response.json()
        setMessage({ type: 'success', text: 'House data updated successfully!' })
        setOriginalHouseData(JSON.parse(JSON.stringify(houseData)))
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to update house data' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error updating house data: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  const updateTaxRates = async () => {
    if (!taxRates) return

    setIsLoading(true)
    try {
      const apiUrl = getAPIUrl(API_CONFIG.endpoints.adminTaxRates)
      const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taxRates)
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Tax rates updated successfully!' })
        setOriginalTaxRates(JSON.parse(JSON.stringify(taxRates)))
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to update tax rates' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error updating tax rates: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  const backupConfiguration = async () => {
    setIsLoading(true)
    try {
      const apiUrl = getAPIUrl(API_CONFIG.endpoints.adminBackup)
      const response = await fetch(apiUrl)
      if (response.ok) {
        const backup = await response.json()
        
        // Download as JSON file
        const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `financial-config-backup-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        setMessage({ type: 'success', text: 'Configuration backup downloaded!' })
      } else {
        setMessage({ type: 'error', text: 'Failed to create backup' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error creating backup: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  const hasHouseChanges = () => {
    return JSON.stringify(houseData) !== JSON.stringify(originalHouseData)
  }

  const hasTaxChanges = () => {
    return JSON.stringify(taxRates) !== JSON.stringify(originalTaxRates)
  }

  const updateHouseField = (houseType: 'house' | 'new_house', field: string, value: any) => {
    if (!houseData) return
    
    setHouseData({
      ...houseData,
      [houseType]: {
        ...houseData[houseType],
        [field]: value
      }
    })
  }

  const updateTaxRate = (field: string, value: number) => {
    if (!taxRates) return
    
    setTaxRates({
      ...taxRates,
      [field]: value
    })
  }

  if (isLoading && !houseData && !taxRates) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading configuration...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Financial Configuration Admin
              </h1>
              <p className="text-muted-foreground mt-1">
                Manage financial planning configuration and settings
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button 
                variant="outline"
                onClick={() => router.push('/')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <Button variant="outline" onClick={backupConfiguration} disabled={isLoading}>
                <Download className="h-4 w-4 mr-2" />
                Backup Config
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Status Message */}
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-6 p-4 rounded-lg border ${
              message.type === 'success' 
                ? 'bg-green-50 border-green-200 text-green-800' 
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            <div className="flex items-center">
              {message.type === 'success' ? (
                <CheckCircle className="h-5 w-5 mr-2" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-2" />
              )}
              {message.text}
            </div>
          </motion.div>
        )}

        <Tabs defaultValue="houses" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="houses">
              <Home className="h-4 w-4 mr-2" />
              House Configuration
            </TabsTrigger>
            <TabsTrigger value="taxes">
              <Receipt className="h-4 w-4 mr-2" />
              Tax Rates
            </TabsTrigger>
            <TabsTrigger value="backup">
              <Settings className="h-4 w-4 mr-2" />
              Backup & Restore
            </TabsTrigger>
          </TabsList>

          {/* House Configuration */}
          <TabsContent value="houses">
            {houseData && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">House Configuration</h2>
                  <div className="flex items-center space-x-2">
                    {hasHouseChanges() && (
                      <Badge variant="outline" className="text-orange-600">
                        Unsaved Changes
                      </Badge>
                    )}
                    <Button 
                      onClick={updateHouseData} 
                      disabled={isLoading || !hasHouseChanges()}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </Button>
                  </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  {/* Current House */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Current House (SF)</CardTitle>
                      <CardDescription>{houseData.house.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="house-value">Property Value</Label>
                          <Input
                            id="house-value"
                            type="number"
                            value={houseData.house.value}
                            onChange={(e) => updateHouseField('house', 'value', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="house-mortgage">Mortgage Principal</Label>
                          <Input
                            id="house-mortgage"
                            type="number"
                            value={houseData.house.mortgage_principal}
                            onChange={(e) => updateHouseField('house', 'mortgage_principal', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="house-payment">Monthly Payment</Label>
                          <Input
                            id="house-payment"
                            type="number"
                            value={houseData.house.monthly_payment}
                            onChange={(e) => updateHouseField('house', 'monthly_payment', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="house-tax">Annual Property Tax</Label>
                          <Input
                            id="house-tax"
                            type="number"
                            value={houseData.house.annual_property_tax}
                            onChange={(e) => updateHouseField('house', 'annual_property_tax', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="house-rate">Interest Rate (%)</Label>
                          <Input
                            id="house-rate"
                            type="number"
                            step="0.001"
                            value={houseData.house.interest_rate}
                            onChange={(e) => updateHouseField('house', 'interest_rate', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="house-growth">Growth Rate (%)</Label>
                          <Input
                            id="house-growth"
                            type="number"
                            step="0.001"
                            value={houseData.house.annual_growth_rate}
                            onChange={(e) => updateHouseField('house', 'annual_growth_rate', parseFloat(e.target.value))}
                          />
                        </div>
                      </div>
                      
                      <div className="pt-4 border-t">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Net Equity:</span>
                            <span className="ml-2 font-medium">
                              {formatCurrency(houseData.house.value - houseData.house.mortgage_principal)}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Payments Made:</span>
                            <span className="ml-2 font-medium">
                              {houseData.house.payments_made}/{houseData.house.number_of_payments}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Future House */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Future Purchase</CardTitle>
                      <CardDescription>{houseData.new_house.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="new-house-value">Property Value</Label>
                          <Input
                            id="new-house-value"
                            type="number"
                            value={houseData.new_house.value}
                            onChange={(e) => updateHouseField('new_house', 'value', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-house-mortgage">Mortgage Principal</Label>
                          <Input
                            id="new-house-mortgage"
                            type="number"
                            value={houseData.new_house.mortgage_principal}
                            onChange={(e) => updateHouseField('new_house', 'mortgage_principal', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-house-payment">Monthly Payment</Label>
                          <Input
                            id="new-house-payment"
                            type="number"
                            value={houseData.new_house.monthly_payment}
                            onChange={(e) => updateHouseField('new_house', 'monthly_payment', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-house-tax">Annual Property Tax</Label>
                          <Input
                            id="new-house-tax"
                            type="number"
                            value={houseData.new_house.annual_property_tax}
                            onChange={(e) => updateHouseField('new_house', 'annual_property_tax', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-house-rate">Interest Rate (%)</Label>
                          <Input
                            id="new-house-rate"
                            type="number"
                            step="0.001"
                            value={houseData.new_house.interest_rate}
                            onChange={(e) => updateHouseField('new_house', 'interest_rate', parseFloat(e.target.value))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-house-growth">Growth Rate (%)</Label>
                          <Input
                            id="new-house-growth"
                            type="number"
                            step="0.001"
                            value={houseData.new_house.annual_growth_rate}
                            onChange={(e) => updateHouseField('new_house', 'annual_growth_rate', parseFloat(e.target.value))}
                          />
                        </div>
                      </div>
                      
                      <div className="pt-4 border-t">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Net Equity:</span>
                            <span className="ml-2 font-medium">
                              {formatCurrency(houseData.new_house.value - houseData.new_house.mortgage_principal)}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Cost Basis:</span>
                            <span className="ml-2 font-medium">
                              {formatCurrency(houseData.new_house.cost_basis)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </TabsContent>

          {/* Tax Rates */}
          <TabsContent value="taxes">
            {taxRates && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">Tax Rate Configuration</h2>
                  <div className="flex items-center space-x-2">
                    {hasTaxChanges() && (
                      <Badge variant="outline" className="text-orange-600">
                        Unsaved Changes
                      </Badge>
                    )}
                    <Button 
                      onClick={updateTaxRates} 
                      disabled={isLoading || !hasTaxChanges()}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </Button>
                  </div>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Tax Rate Settings</CardTitle>
                    <CardDescription>Configure tax rates for financial projections</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="tax-assumed">Assumed Rate</Label>
                        <Input
                          id="tax-assumed"
                          type="number"
                          step="0.0001"
                          value={taxRates.assumed}
                          onChange={(e) => updateTaxRate('assumed', parseFloat(e.target.value))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatPercentage(taxRates.assumed)}
                        </p>
                      </div>
                      <div>
                        <Label htmlFor="tax-federal-single">Federal Single</Label>
                        <Input
                          id="tax-federal-single"
                          type="number"
                          step="0.0001"
                          value={taxRates.federal_single}
                          onChange={(e) => updateTaxRate('federal_single', parseFloat(e.target.value))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatPercentage(taxRates.federal_single)}
                        </p>
                      </div>
                      <div>
                        <Label htmlFor="tax-state-single">State Single</Label>
                        <Input
                          id="tax-state-single"
                          type="number"
                          step="0.0001"
                          value={taxRates.state_single}
                          onChange={(e) => updateTaxRate('state_single', parseFloat(e.target.value))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatPercentage(taxRates.state_single)}
                        </p>
                      </div>
                      <div>
                        <Label htmlFor="tax-federal-dual">Federal Dual</Label>
                        <Input
                          id="tax-federal-dual"
                          type="number"
                          step="0.0001"
                          value={taxRates.federal_dual}
                          onChange={(e) => updateTaxRate('federal_dual', parseFloat(e.target.value))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatPercentage(taxRates.federal_dual)}
                        </p>
                      </div>
                      <div>
                        <Label htmlFor="tax-state-dual">State Dual</Label>
                        <Input
                          id="tax-state-dual"
                          type="number"
                          step="0.0001"
                          value={taxRates.state_dual}
                          onChange={(e) => updateTaxRate('state_dual', parseFloat(e.target.value))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatPercentage(taxRates.state_dual)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Backup & Restore */}
          <TabsContent value="backup">
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold">Backup & Restore</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Configuration Backup</CardTitle>
                  <CardDescription>Download a complete backup of your financial configuration</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button onClick={backupConfiguration} disabled={isLoading}>
                    <Download className="h-4 w-4 mr-2" />
                    Download Backup
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Configuration Restore</CardTitle>
                  <CardDescription>Restore configuration from a backup file (coming soon)</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" disabled>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload & Restore
                  </Button>
                  <p className="text-sm text-muted-foreground mt-2">
                    File upload functionality will be implemented in a future update.
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}