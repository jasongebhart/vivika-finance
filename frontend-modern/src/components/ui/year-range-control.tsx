'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'
import { ClientWrapper } from '@/components/client-wrapper'
import { Calendar, ChevronDown, ChevronUp, Settings, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

// Predefined year range options
export const YEAR_RANGE_PRESETS = [
  { years: 1, label: '1 Year', description: 'Immediate planning', color: 'bg-red-500' },
  { years: 2, label: '2 Years', description: 'Short-term decisions', color: 'bg-orange-500' },
  { years: 3, label: '3 Years', description: 'Medium-term planning', color: 'bg-yellow-500' },
  { years: 5, label: '5 Years', description: 'Major life changes', color: 'bg-green-500' },
  { years: 8, label: '8 Years', description: 'Long-term goals', color: 'bg-blue-500' },
  { years: 10, label: '10 Years', description: 'Decade planning', color: 'bg-indigo-500' },
  { years: 15, label: '15 Years', description: 'Mid-career goals', color: 'bg-purple-500' },
  { years: 20, label: '20 Years', description: 'Pre-retirement', color: 'bg-pink-500' },
  { years: 30, label: '30 Years', description: 'Full retirement plan', color: 'bg-slate-500' },
  { years: 50, label: '50 Years', description: 'Generational wealth', color: 'bg-emerald-500' }
] as const

export interface YearRangeControlProps {
  value: number
  onChange: (years: number) => void
  startYear?: number
  onStartYearChange?: (year: number) => void
  showStartYear?: boolean
  showAdvanced?: boolean
  className?: string
  compact?: boolean
  disabled?: boolean
  min?: number
  max?: number
}

export function YearRangeControl({
  value,
  onChange,
  startYear = new Date().getFullYear(),
  onStartYearChange,
  showStartYear = true,
  showAdvanced = true,
  className,
  compact = false,
  disabled = false,
  min = 1,
  max = 50
}: YearRangeControlProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [customYears, setCustomYears] = useState(value.toString())

  // Update custom years when value changes externally
  useEffect(() => {
    if (value.toString() !== customYears) {
      setCustomYears(value.toString())
    }
  }, [value, customYears])

  const selectedPreset = useMemo(() => 
    YEAR_RANGE_PRESETS.find(preset => preset.years === value), 
    [value]
  )
  const endYear = useMemo(() => startYear + value - 1, [startYear, value])

  const handlePresetSelect = useCallback((years: number) => {
    onChange(years)
    if (compact) {
      setIsExpanded(false)
    }
  }, [onChange, compact])

  const handleCustomYearChange = useCallback((inputValue: string) => {
    setCustomYears(inputValue)
    const years = parseInt(inputValue)
    if (!isNaN(years) && years >= min && years <= max) {
      onChange(years)
    }
  }, [onChange, min, max])

  const handleStartYearChange = useCallback((inputValue: string) => {
    const year = parseInt(inputValue)
    if (!isNaN(year) && year >= 2020 && year <= 2050 && onStartYearChange) {
      onStartYearChange(year)
    }
  }, [onStartYearChange])

  const resetToDefault = useCallback(() => {
    onChange(5) // Default to 5 years
    if (onStartYearChange) {
      onStartYearChange(new Date().getFullYear())
    }
  }, [onChange, onStartYearChange])

  if (compact) {
    return (
      <ClientWrapper 
        fallback={
          <Button variant="outline" disabled className="h-9 px-3">
            <Calendar className="h-4 w-4 mr-2" />
            <span className="font-medium">5 Years</span>
            <ChevronDown className="h-4 w-4 ml-2" />
          </Button>
        }
      >
        <div className={cn("relative", className)}>
          <Button
            variant="outline"
            onClick={() => setIsExpanded(!isExpanded)}
            disabled={disabled}
            className="h-9 px-3"
          >
            <Calendar className="h-4 w-4 mr-2" />
            <span className="font-medium">{value} Year{value !== 1 ? 's' : ''}</span>
            {isExpanded ? <ChevronUp className="h-4 w-4 ml-2" /> : <ChevronDown className="h-4 w-4 ml-2" />}
          </Button>

        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 z-50 mt-2 w-80"
          >
            <Card className="shadow-lg border">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-sm">Select Time Range</CardTitle>
                    <CardDescription className="text-xs">
                      {startYear} - {endYear} ({value} years)
                    </CardDescription>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={resetToDefault}
                    className="h-7 w-7 p-0"
                  >
                    <RotateCcw className="h-3 w-3" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  {YEAR_RANGE_PRESETS.slice(0, 6).map((preset) => (
                    <Button
                      key={preset.years}
                      variant={value === preset.years ? "default" : "outline"}
                      size="sm"
                      onClick={() => handlePresetSelect(preset.years)}
                      className="h-8 text-xs"
                    >
                      {preset.label}
                    </Button>
                  ))}
                </div>
                
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    min={min}
                    max={max}
                    value={customYears}
                    onChange={(e) => handleCustomYearChange(e.target.value)}
                    className="h-8 text-sm"
                    placeholder="Custom years"
                  />
                  <span className="text-xs text-muted-foreground">years</span>
                </div>

                {showStartYear && onStartYearChange && (
                  <div className="flex items-center space-x-2 pt-2 border-t">
                    <span className="text-xs text-muted-foreground">Start:</span>
                    <Input
                      type="number"
                      min={2020}
                      max={2050}
                      value={startYear}
                      onChange={(e) => handleStartYearChange(e.target.value)}
                      className="h-8 w-20 text-sm"
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
        </div>
      </ClientWrapper>
    )
  }

  return (
    <ClientWrapper 
      fallback={
        <Card className={cn("", className)}>
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Calendar className="h-5 w-5 mr-2" />
              Time Range Selection
            </CardTitle>
            <CardDescription>
              Planning horizon: {new Date().getFullYear()} - {new Date().getFullYear() + 4} (5 years)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center text-muted-foreground py-4">
              Loading year range controls...
            </div>
          </CardContent>
        </Card>
      }
    >
      <Card className={cn("", className)}>
        <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center text-lg">
              <Calendar className="h-5 w-5 mr-2" />
              Time Range Selection
            </CardTitle>
            <CardDescription>
              Planning horizon: {startYear} - {endYear} ({value} years)
            </CardDescription>
          </div>
          {showAdvanced && (
            <div className="flex items-center space-x-2">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={resetToDefault}
                disabled={disabled}
              >
                <RotateCcw className="h-4 w-4 mr-1" />
                Reset
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                disabled={disabled}
              >
                <Settings className="h-4 w-4 mr-1" />
                {isExpanded ? 'Less' : 'More'}
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Current Selection Display */}
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
          <div>
            <div className="font-medium">Selected Range</div>
            <div className="text-sm text-muted-foreground">
              {selectedPreset?.description || 'Custom timeline'}
            </div>
          </div>
          <Badge variant="secondary" className="text-sm font-medium">
            {value} Year{value !== 1 ? 's' : ''}
          </Badge>
        </div>

        {/* Quick Preset Buttons */}
        <div>
          <div className="mb-2 text-sm font-medium">Quick Options</div>
          <div className="grid grid-cols-3 gap-2">
            {YEAR_RANGE_PRESETS.slice(0, 6).map((preset) => (
              <Button
                key={preset.years}
                variant={value === preset.years ? "default" : "outline"}
                size="sm"
                onClick={() => handlePresetSelect(preset.years)}
                disabled={disabled}
                className="h-9"
              >
                {preset.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Custom Input */}
        <div className="space-y-2">
          <div className="text-sm font-medium">Custom Range</div>
          <div className="flex items-center space-x-2">
            <Input
              type="number"
              min={min}
              max={max}
              value={customYears}
              onChange={(e) => handleCustomYearChange(e.target.value)}
              disabled={disabled}
              className="flex-1"
              placeholder="Enter number of years"
            />
            <span className="text-sm text-muted-foreground">years</span>
          </div>
        </div>

        {/* Advanced Options */}
        {isExpanded && showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4 pt-4 border-t"
          >
            {/* Extended Presets */}
            <div>
              <div className="mb-2 text-sm font-medium">Extended Options</div>
              <div className="grid grid-cols-2 gap-2">
                {YEAR_RANGE_PRESETS.slice(6).map((preset) => (
                  <Button
                    key={preset.years}
                    variant={value === preset.years ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePresetSelect(preset.years)}
                    disabled={disabled}
                    className="h-8 text-xs"
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Start Year Control */}
            {showStartYear && onStartYearChange && (
              <div className="space-y-2">
                <div className="text-sm font-medium">Start Year</div>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    min={2020}
                    max={2050}
                    value={startYear}
                    onChange={(e) => handleStartYearChange(e.target.value)}
                    disabled={disabled}
                    className="w-24"
                  />
                  <span className="text-sm text-muted-foreground">to {endYear}</span>
                </div>
              </div>
            )}

            {/* Range Info */}
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="text-sm">
                <strong>Planning Period:</strong> {startYear} - {endYear}<br />
                <strong>Duration:</strong> {value} year{value !== 1 ? 's' : ''}<br />
                <strong>Use Case:</strong> {selectedPreset?.description || 'Custom planning timeline'}
              </div>
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
    </ClientWrapper>
  )
}

// Hook for managing year range state
export function useYearRange(initialYears: number = 5, initialStartYear?: number) {
  const [years, setYears] = useState(initialYears)
  const [startYear, setStartYear] = useState(initialStartYear || new Date().getFullYear())

  const endYear = startYear + years - 1

  const generateYearRange = () => {
    return Array.from({ length: years }, (_, i) => startYear + i)
  }

  const isYearInRange = (year: number) => {
    return year >= startYear && year <= endYear
  }

  const filterDataByYearRange = <T extends { year?: number; age?: number }>(
    data: T[], 
    currentAge?: number
  ): T[] => {
    if (!data.length) return data

    return data.filter((item) => {
      if (item.year !== undefined) {
        return isYearInRange(item.year)
      }
      if (item.age !== undefined && currentAge !== undefined) {
        const itemYear = startYear + (item.age - currentAge)
        return isYearInRange(itemYear)
      }
      return true
    })
  }

  return {
    years,
    setYears,
    startYear,
    setStartYear,
    endYear,
    yearRange: generateYearRange(),
    isYearInRange,
    filterDataByYearRange
  }
}