'use client'

import { useMemo } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatCurrency } from '@/lib/utils'
import type { ScenarioProjection, MonteCarloResults } from '@/types'

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { 
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[400px]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  )
})

interface Advanced3DChartProps {
  data: ScenarioProjection[]
  title: string
  description: string
  className?: string
}

export function Advanced3DProjectionChart({ data, title, description, className }: Advanced3DChartProps) {
  const chartData = useMemo(() => {
    if (!data.length) return { x: [], y: [], z: [], text: [] }
    
    const x: number[] = []
    const y: number[] = []
    const z: number[] = []
    const text: string[] = []
    
    data.forEach((scenario, scenarioIndex) => {
      scenario.yearly_projections.forEach((projection) => {
        x.push(projection.year)
        y.push(scenarioIndex)
        z.push(projection.net_worth)
        text.push(`Scenario ${scenarioIndex + 1}<br>Year: ${projection.year}<br>Net Worth: ${formatCurrency(projection.net_worth)}`)
      })
    })
    
    return { x, y, z, text }
  }, [data])

  const plotData = [{
    x: chartData.x,
    y: chartData.y,
    z: chartData.z,
    text: chartData.text,
    type: 'scatter3d' as const,
    mode: 'lines+markers' as const,
    marker: {
      size: 4,
      color: chartData.z,
      colorscale: 'Viridis',
      colorbar: {
        title: { text: 'Net Worth' },
        tickformat: '$,.0f'
      } as any
    },
    line: {
      color: 'rgba(127, 127, 127, 0.6)',
      width: 2
    },
    hovertemplate: '%{text}<extra></extra>'
  }]

  const layout = {
    title: {
      text: title,
      font: { size: 16 }
    },
    scene: {
      xaxis: {
        title: 'Year',
        titlefont: { size: 12 }
      },
      yaxis: {
        title: 'Scenario',
        titlefont: { size: 12 }
      },
      zaxis: {
        title: 'Net Worth ($)',
        titlefont: { size: 12 },
        tickformat: '$,.0f'
      },
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 }
      }
    },
    margin: { l: 0, r: 0, b: 0, t: 40 },
    height: 500,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  }

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] as any,
    responsive: true
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '100%' }}
        />
      </CardContent>
    </Card>
  )
}

interface MonteCarloSurfaceChartProps {
  data: MonteCarloResults
  className?: string
}

export function MonteCarloSurfaceChart({ data, className }: MonteCarloSurfaceChartProps) {
  const surfaceData = useMemo(() => {
    if (!data.simulations.length) return { x: [], y: [], z: [] }
    
    // Create a probability density surface
    const years = Array.from({ length: data.simulations[0].yearly_values.length }, (_, i) => 
      new Date().getFullYear() + i
    )
    
    // Create value bins for each year
    const valueBins = 50
    const yearData = years.map(year => {
      const yearIndex = year - new Date().getFullYear()
      const values = data.simulations.map(sim => sim.yearly_values[yearIndex])
      const minVal = Math.min(...values)
      const maxVal = Math.max(...values)
      const binSize = (maxVal - minVal) / valueBins
      
      const bins = Array.from({ length: valueBins }, (_, i) => minVal + i * binSize)
      const densities = bins.map(binValue => {
        const count = values.filter(val => 
          val >= binValue && val < binValue + binSize
        ).length
        return count / values.length / binSize // Normalize to density
      })
      
      return { year, bins, densities }
    })
    
    const x = years
    const y = yearData[0].bins
    const z = yearData.map(yd => yd.densities)
    
    return { x, y, z }
  }, [data.simulations])

  const plotData = [{
    x: surfaceData.x,
    y: surfaceData.y,
    z: surfaceData.z,
    type: 'surface' as const,
    colorscale: 'Viridis',
    showscale: true,
    colorbar: {
      title: { text: 'Probability Density' },
      titleside: 'right'
    } as any,
    hovertemplate: 'Year: %{x}<br>Value: $%{y:,.0f}<br>Density: %{z:.6f}<extra></extra>'
  }]

  const layout = {
    title: {
      text: 'Monte Carlo Probability Surface',
      font: { size: 16 }
    },
    scene: {
      xaxis: {
        title: 'Year',
        titlefont: { size: 12 }
      },
      yaxis: {
        title: 'Portfolio Value ($)',
        titlefont: { size: 12 },
        tickformat: '$,.0f'
      },
      zaxis: {
        title: 'Probability Density',
        titlefont: { size: 12 }
      },
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 }
      }
    },
    margin: { l: 0, r: 0, b: 0, t: 40 },
    height: 600,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  }

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] as any,
    responsive: true
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Monte Carlo Probability Surface</CardTitle>
        <CardDescription>
          3D visualization of outcome probabilities across time and portfolio values
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '100%' }}
        />
      </CardContent>
    </Card>
  )
}

interface InteractiveScatterPlotProps {
  data: {
    scenarios: Array<{
      id: string
      name: string
      finalNetWorth: number
      totalContributions: number
      riskLevel: number
      scenario_type: string
    }>
  }
  className?: string
}

export function InteractiveScatterPlot({ data, className }: InteractiveScatterPlotProps) {
  const plotData = useMemo(() => {
    const colors = {
      current: '#3b82f6',
      retirement: '#10b981',
      relocation: '#f59e0b',
      education: '#8b5cf6',
      major_purchase: '#ef4444'
    }
    
    return data.scenarios.map(scenario => ({
      x: [scenario.totalContributions],
      y: [scenario.finalNetWorth],
      mode: 'markers' as const,
      type: 'scatter' as const,
      name: scenario.name,
      marker: {
        size: Math.sqrt(scenario.riskLevel) * 10 + 10,
        color: colors[scenario.scenario_type as keyof typeof colors] || '#6b7280',
        opacity: 0.7,
        line: {
          color: 'white',
          width: 2
        }
      },
      text: `${scenario.name}<br>Risk Level: ${scenario.riskLevel}<br>Type: ${scenario.scenario_type}`,
      hovertemplate: '%{text}<br>Contributions: $%{x:,.0f}<br>Final Net Worth: $%{y:,.0f}<extra></extra>'
    }))
  }, [data.scenarios])

  const layout = {
    title: {
      text: 'Scenario Risk vs. Return Analysis',
      font: { size: 16 }
    },
    xaxis: {
      title: 'Total Contributions ($)',
      tickformat: '$,.0f',
      gridcolor: 'rgba(128,128,128,0.2)'
    },
    yaxis: {
      title: 'Final Net Worth ($)',
      tickformat: '$,.0f',
      gridcolor: 'rgba(128,128,128,0.2)'
    },
    hovermode: 'closest' as const,
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(255,255,255,0.8)',
      bordercolor: 'rgba(0,0,0,0.2)',
      borderwidth: 1
    },
    margin: { l: 80, r: 40, b: 80, t: 60 },
    height: 500,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  }

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] as any,
    responsive: true
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Scenario Comparison Analysis</CardTitle>
        <CardDescription>
          Interactive scatter plot comparing total contributions vs. final outcomes. Bubble size represents risk level.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '100%' }}
        />
      </CardContent>
    </Card>
  )
}

interface CorrelationHeatmapProps {
  data: {
    variables: string[]
    correlationMatrix: number[][]
  }
  className?: string
}

export function CorrelationHeatmap({ data, className }: CorrelationHeatmapProps) {
  const plotData = [{
    x: data.variables,
    y: data.variables,
    z: data.correlationMatrix,
    type: 'heatmap' as const,
    colorscale: 'RdBu',
    zmid: 0,
    colorbar: {
      title: { text: 'Correlation' },
      titleside: 'right'
    } as any,
    hovertemplate: '%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>',
    text: data.correlationMatrix.map(row => 
      row.map(val => val.toFixed(3))
    ) as any,
    texttemplate: '%{text}',
    textfont: { color: 'white', size: 10 }
  }]

  const layout = {
    title: {
      text: 'Financial Variables Correlation Matrix',
      font: { size: 16 }
    },
    xaxis: {
      title: '',
      tickangle: -45
    },
    yaxis: {
      title: ''
    },
    margin: { l: 100, r: 40, b: 100, t: 60 },
    height: 500,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  }

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] as any,
    responsive: true
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Variable Correlation Analysis</CardTitle>
        <CardDescription>
          Correlation matrix showing relationships between key financial variables
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '100%' }}
        />
      </CardContent>
    </Card>
  )
}