'use client'

import { useEffect, useState, useMemo } from 'react'

interface ClientWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ClientWrapper({ children, fallback = null }: ClientWrapperProps) {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  // Memoize the fallback to prevent unnecessary re-renders
  const memoizedFallback = useMemo(() => fallback, [fallback])

  if (!isClient) {
    return <>{memoizedFallback}</>
  }

  return <>{children}</>
}