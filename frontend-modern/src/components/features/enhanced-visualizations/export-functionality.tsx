'use client'

import { useState, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  Download,
  FileText,
  Table,
  Image,
  Mail,
  Share2,
  Printer,
  Settings,
  Eye,
  Calendar
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface ExportData {
  scenarios: Array<{
    id: string
    name: string
    results: {
      final_net_worth: number
      annual_growth_rate: number
      total_expenses: number
      retirement_readiness: boolean
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
  analysis: {
    bestScenario: string
    worstScenario: string
    avgGrowthRate: number
    totalScenarios: number
  }
}

interface ExportFunctionalityProps {
  data: ExportData
  className?: string
}

interface ExportOptions {
  includeCharts: boolean
  includeDetailedProjections: boolean
  includeScenarioComparison: boolean
  includeTrendAnalysis: boolean
  includeRecommendations: boolean
  format: 'pdf' | 'excel' | 'csv' | 'png'
  template: 'detailed' | 'summary' | 'executive'
}

export function ExportFunctionality({ data, className = '' }: ExportFunctionalityProps) {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    includeCharts: true,
    includeDetailedProjections: true,
    includeScenarioComparison: true,
    includeTrendAnalysis: false,
    includeRecommendations: true,
    format: 'pdf',
    template: 'detailed'
  })
  
  const [isExporting, setIsExporting] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const printRef = useRef<HTMLDivElement>(null)

  const handleExport = async (format: string) => {
    setIsExporting(true)
    
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      if (format === 'pdf') {
        await exportToPDF()
      } else if (format === 'excel') {
        await exportToExcel()
      } else if (format === 'csv') {
        await exportToCSV()
      } else if (format === 'png') {
        await exportToImage()
      }
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  const exportToPDF = async () => {
    // In a real implementation, you would use a library like jsPDF or react-pdf
    const reportContent = generateReportContent()
    
    // Simulate PDF generation
    const blob = new Blob([reportContent], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `vivika-finance-analysis-${new Date().toISOString().split('T')[0]}.pdf`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportToExcel = async () => {
    // In a real implementation, you would use a library like SheetJS
    const excelData = generateExcelData()
    
    const csvContent = convertToCSV(excelData)
    const blob = new Blob([csvContent], { type: 'application/vnd.ms-excel' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `vivika-finance-data-${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportToCSV = async () => {
    const csvData = generateCSVData()
    const blob = new Blob([csvData], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `vivika-finance-projections-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportToImage = async () => {
    // In a real implementation, you would use html2canvas or similar
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (ctx) {
      canvas.width = 1200
      canvas.height = 800
      ctx.fillStyle = 'white'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      ctx.fillStyle = 'black'
      ctx.font = '24px Arial'
      ctx.fillText('VivikA Finance - Analysis Report', 50, 50)
      
      ctx.font = '16px Arial'
      ctx.fillText(`Generated: ${new Date().toLocaleDateString()}`, 50, 100)
      ctx.fillText(`Best Scenario: ${data.analysis.bestScenario}`, 50, 130)
      ctx.fillText(`Average Growth: ${(data.analysis.avgGrowthRate * 100).toFixed(1)}%`, 50, 160)
    }
    
    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `vivika-finance-snapshot-${new Date().toISOString().split('T')[0]}.png`
        link.click()
        URL.revokeObjectURL(url)
      }
    })
  }

  const generateReportContent = () => {
    const currentDate = new Date().toLocaleDateString()
    
    return `
VivikA Finance - Financial Analysis Report
Generated: ${currentDate}

EXECUTIVE SUMMARY
================

Total Scenarios Analyzed: ${data.analysis.totalScenarios}
Best Performing Scenario: ${data.analysis.bestScenario}
Average Growth Rate: ${(data.analysis.avgGrowthRate * 100).toFixed(1)}%

SCENARIO ANALYSIS
================

${data.scenarios.map(scenario => `
Scenario: ${scenario.name}
Location: ${scenario.parameters.location}
Housing: ${scenario.parameters.housing}
School Type: ${scenario.parameters.schoolType}
Spouse Status: ${scenario.parameters.spouse1Status} / ${scenario.parameters.spouse2Status}

Results:
- Final Net Worth: ${formatCurrency(scenario.results.final_net_worth)}
- Annual Growth Rate: ${(scenario.results.annual_growth_rate * 100).toFixed(1)}%
- Total Expenses: ${formatCurrency(scenario.results.total_expenses)}
- Retirement Ready: ${scenario.results.retirement_readiness ? 'Yes' : 'No'}

`).join('')}

${exportOptions.includeDetailedProjections ? `
DETAILED PROJECTIONS
===================

${data.scenarios.map(scenario => 
  scenario.results.yearly_projections?.map(proj => 
    `${proj.year}: Net Worth ${formatCurrency(proj.net_worth)}, Income ${formatCurrency(proj.income)}, Expenses ${formatCurrency(proj.expenses)}`
  ).join('\n') || ''
).join('\n\n')}
` : ''}

Report generated by VivikA Finance Analysis Tool
`
  }

  const generateExcelData = () => {
    return data.scenarios.map(scenario => ({
      'Scenario Name': scenario.name,
      'Location': scenario.parameters.location,
      'Housing': scenario.parameters.housing,
      'School Type': scenario.parameters.schoolType,
      'Spouse 1 Status': scenario.parameters.spouse1Status,
      'Spouse 2 Status': scenario.parameters.spouse2Status,
      'Final Net Worth': scenario.results.final_net_worth,
      'Annual Growth Rate': scenario.results.annual_growth_rate,
      'Total Expenses': scenario.results.total_expenses,
      'Retirement Ready': scenario.results.retirement_readiness ? 'Yes' : 'No'
    }))
  }

  const generateCSVData = () => {
    const headers = ['Year', 'Age', 'Scenario', 'Net Worth', 'Income', 'Expenses', 'Net Cash Flow']
    const rows = [headers.join(',')]
    
    data.scenarios.forEach(scenario => {
      scenario.results.yearly_projections?.forEach(proj => {
        rows.push([
          proj.year,
          proj.age,
          scenario.name,
          proj.net_worth,
          proj.income,
          proj.expenses,
          proj.net_cash_flow
        ].join(','))
      })
    })
    
    return rows.join('\n')
  }

  const convertToCSV = (data: any[]) => {
    if (!data.length) return ''
    
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map(row => Object.values(row).join(','))
    
    return [headers, ...rows].join('\n')
  }

  const handlePrint = () => {
    window.print()
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'VivikA Finance Analysis',
          text: `Financial analysis showing ${data.analysis.totalScenarios} scenarios with ${(data.analysis.avgGrowthRate * 100).toFixed(1)}% average growth`,
          url: window.location.href
        })
      } catch (error) {
        console.error('Share failed:', error)
      }
    } else {
      // Fallback - copy to clipboard
      navigator.clipboard.writeText(window.location.href)
    }
  }

  const getEstimatedFileSize = () => {
    let size = 0
    if (exportOptions.includeCharts) size += 2 // MB
    if (exportOptions.includeDetailedProjections) size += 1
    if (exportOptions.includeScenarioComparison) size += 0.5
    if (exportOptions.includeTrendAnalysis) size += 1.5
    if (exportOptions.includeRecommendations) size += 0.3
    
    return Math.max(0.1, size).toFixed(1)
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Export Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Download className="h-5 w-5 mr-2" />
            Export & Share Analysis
          </CardTitle>
          <CardDescription>
            Generate comprehensive reports and share your financial analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Format Selection */}
          <div className="space-y-3">
            <h4 className="font-medium">Export Format</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { id: 'pdf', label: 'PDF Report', icon: FileText, description: 'Complete formatted report' },
                { id: 'excel', label: 'Excel Data', icon: Table, description: 'Spreadsheet with all data' },
                { id: 'csv', label: 'CSV Data', icon: Table, description: 'Raw data for analysis' },
                { id: 'png', label: 'Image', icon: Image, description: 'Visual snapshot' }
              ].map(format => (
                <Card 
                  key={format.id}
                  className={`cursor-pointer transition-colors ${
                    exportOptions.format === format.id ? 'ring-2 ring-primary' : ''
                  }`}
                  onClick={() => setExportOptions(prev => ({ ...prev, format: format.id as any }))}
                >
                  <CardContent className="pt-4 text-center">
                    <format.icon className="h-8 w-8 mx-auto mb-2 text-primary" />
                    <div className="font-medium text-sm">{format.label}</div>
                    <div className="text-xs text-muted-foreground">{format.description}</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Content Options */}
          <div className="space-y-3">
            <h4 className="font-medium">Include in Export</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'includeCharts', label: 'Charts & Visualizations', description: 'All graphs and charts' },
                { key: 'includeDetailedProjections', label: 'Detailed Projections', description: 'Year-by-year data' },
                { key: 'includeScenarioComparison', label: 'Scenario Comparison', description: 'Side-by-side analysis' },
                { key: 'includeTrendAnalysis', label: 'Trend Analysis', description: 'Advanced analytics' },
                { key: 'includeRecommendations', label: 'Recommendations', description: 'AI-generated insights' }
              ].map(option => (
                <div key={option.key} className="flex items-start space-x-3">
                  <Checkbox
                    id={option.key}
                    checked={exportOptions[option.key as keyof ExportOptions] as boolean}
                    onCheckedChange={(checked) => 
                      setExportOptions(prev => ({ 
                        ...prev, 
                        [option.key]: checked 
                      }))
                    }
                  />
                  <div className="space-y-1">
                    <label htmlFor={option.key} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      {option.label}
                    </label>
                    <p className="text-xs text-muted-foreground">
                      {option.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Template Selection */}
          <div className="space-y-3">
            <h4 className="font-medium">Report Template</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { id: 'detailed', label: 'Detailed Report', description: 'Complete analysis with all sections' },
                { id: 'summary', label: 'Summary Report', description: 'Key insights and highlights' },
                { id: 'executive', label: 'Executive Summary', description: 'High-level overview for decision makers' }
              ].map(template => (
                <Card 
                  key={template.id}
                  className={`cursor-pointer transition-colors ${
                    exportOptions.template === template.id ? 'ring-2 ring-primary' : ''
                  }`}
                  onClick={() => setExportOptions(prev => ({ ...prev, template: template.id as any }))}
                >
                  <CardContent className="pt-4">
                    <div className="font-medium text-sm mb-1">{template.label}</div>
                    <div className="text-xs text-muted-foreground">{template.description}</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Export Info */}
          <div className="bg-muted/50 rounded-lg p-4">
            <div className="flex items-center justify-between text-sm">
              <span>Estimated file size:</span>
              <Badge variant="outline">{getEstimatedFileSize()} MB</Badge>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span>Export includes:</span>
              <span>{data.analysis.totalScenarios} scenarios</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              onClick={() => handleExport(exportOptions.format)}
              disabled={isExporting}
              className="w-full"
            >
              <Download className="h-4 w-4 mr-2" />
              {isExporting ? 'Exporting...' : 'Export'}
            </Button>
            
            <Button 
              variant="outline" 
              onClick={() => setShowPreview(!showPreview)}
              className="w-full"
            >
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            
            <Button 
              variant="outline" 
              onClick={handlePrint}
              className="w-full"
            >
              <Printer className="h-4 w-4 mr-2" />
              Print
            </Button>
            
            <Button 
              variant="outline" 
              onClick={handleShare}
              className="w-full"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Quick Export Buttons */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Export</CardTitle>
          <CardDescription>
            Pre-configured export options for common use cases
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              variant="outline" 
              onClick={() => {
                setExportOptions({
                  ...exportOptions,
                  format: 'pdf',
                  template: 'executive',
                  includeCharts: true,
                  includeDetailedProjections: false,
                  includeScenarioComparison: true,
                  includeTrendAnalysis: false,
                  includeRecommendations: true
                })
                handleExport('pdf')
              }}
              className="h-auto py-4 flex-col"
            >
              <Briefcase className="h-6 w-6 mb-2" />
              <span className="font-medium">Executive Summary</span>
              <span className="text-xs text-muted-foreground">For presentations</span>
            </Button>
            
            <Button 
              variant="outline" 
              onClick={() => {
                setExportOptions({
                  ...exportOptions,
                  format: 'excel',
                  template: 'detailed',
                  includeCharts: false,
                  includeDetailedProjections: true,
                  includeScenarioComparison: true,
                  includeTrendAnalysis: true,
                  includeRecommendations: false
                })
                handleExport('excel')
              }}
              className="h-auto py-4 flex-col"
            >
              <Table className="h-6 w-6 mb-2" />
              <span className="font-medium">Data Analysis</span>
              <span className="text-xs text-muted-foreground">For detailed analysis</span>
            </Button>
            
            <Button 
              variant="outline" 
              onClick={() => {
                setExportOptions({
                  ...exportOptions,
                  format: 'pdf',
                  template: 'detailed',
                  includeCharts: true,
                  includeDetailedProjections: true,
                  includeScenarioComparison: true,
                  includeTrendAnalysis: true,
                  includeRecommendations: true
                })
                handleExport('pdf')
              }}
              className="h-auto py-4 flex-col"
            >
              <FileText className="h-6 w-6 mb-2" />
              <span className="font-medium">Complete Report</span>
              <span className="text-xs text-muted-foreground">Everything included</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Preview Modal */}
      {showPreview && (
        <Card>
          <CardHeader>
            <CardTitle>Export Preview</CardTitle>
            <CardDescription>
              Preview of your {exportOptions.format.toUpperCase()} export
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div ref={printRef} className="bg-white p-6 border rounded-lg">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-bold">VivikA Finance Analysis Report</h1>
                <p className="text-muted-foreground">Generated on {new Date().toLocaleDateString()}</p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h2 className="text-lg font-semibold mb-2">Executive Summary</h2>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>Total Scenarios: {data.analysis.totalScenarios}</div>
                    <div>Best Scenario: {data.analysis.bestScenario}</div>
                    <div>Average Growth: {(data.analysis.avgGrowthRate * 100).toFixed(1)}%</div>
                    <div>Analysis Date: {new Date().toLocaleDateString()}</div>
                  </div>
                </div>
                
                {exportOptions.includeScenarioComparison && (
                  <div>
                    <h2 className="text-lg font-semibold mb-2">Scenario Comparison</h2>
                    <div className="overflow-x-auto text-sm">
                      <table className="w-full border-collapse border">
                        <thead>
                          <tr className="bg-muted">
                            <th className="border p-2 text-left">Scenario</th>
                            <th className="border p-2 text-right">Final Net Worth</th>
                            <th className="border p-2 text-right">Growth Rate</th>
                            <th className="border p-2 text-center">Retirement Ready</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.scenarios.map(scenario => (
                            <tr key={scenario.id}>
                              <td className="border p-2">{scenario.name}</td>
                              <td className="border p-2 text-right">{formatCurrency(scenario.results.final_net_worth)}</td>
                              <td className="border p-2 text-right">{(scenario.results.annual_growth_rate * 100).toFixed(1)}%</td>
                              <td className="border p-2 text-center">{scenario.results.retirement_readiness ? '✓' : '✗'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}