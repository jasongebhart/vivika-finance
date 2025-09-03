import { useEffect, useRef, useState } from 'react'
import { getWSUrl } from '@/lib/config'

interface ConfigUpdateMessage {
  type: 'config_update'
  config_type: string
  data: any
  timestamp: string
}

interface ScenarioUpdateMessage {
  type: 'scenario_update'
  scenario_id: string
  action: string
  timestamp: string
}

type WebSocketMessage = ConfigUpdateMessage | ScenarioUpdateMessage

interface UseWebSocketOptions {
  onConfigUpdate?: (configType: string, data: any) => void
  onScenarioUpdate?: (scenarioId: string, action: string) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export function useWebSocket(endpoint: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    try {
      // Check if we're in a browser environment
      if (typeof window === 'undefined') {
        setError('WebSocket not available in server environment')
        return
      }

      const wsUrl = getWSUrl(endpoint)
      
      console.log(`Attempting WebSocket connection to: ${wsUrl}`)
      
      // Add a small delay to ensure backend is ready
      setTimeout(() => {
        wsRef.current = new WebSocket(wsUrl)
        setupWebSocketHandlers()
      }, 100)
      
    } catch (err) {
      setError(`Failed to create WebSocket connection: ${err.message}`)
    }
  }

  const setupWebSocketHandlers = () => {
    if (!wsRef.current) return

    wsRef.current.onopen = () => {
      setIsConnected(true)
      setError(null)
      reconnectAttempts.current = 0
      options.onConnect?.()
      console.log(`WebSocket connected to ${endpoint}`)
      
      // Send ping to keep connection alive
      const pingInterval = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send('ping')
        }
      }, 30000) // Ping every 30 seconds
      
      wsRef.current.pingInterval = pingInterval
    }

    wsRef.current.onmessage = (event) => {
      if (event.data === 'pong') return // Ignore pong responses
      
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        setLastMessage(message)
        
        if (message.type === 'config_update') {
          options.onConfigUpdate?.(message.config_type, message.data)
        } else if (message.type === 'scenario_update') {
          options.onScenarioUpdate?.(message.scenario_id, message.action)
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    wsRef.current.onclose = () => {
      setIsConnected(false)
      options.onDisconnect?.()
      
      // Clear ping interval
      if (wsRef.current?.pingInterval) {
        clearInterval(wsRef.current.pingInterval)
      }
      
      // Attempt reconnection if not intentionally closed
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
        console.log(`WebSocket disconnected. Reconnecting in ${delay}ms...`)
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, delay)
      } else {
        setError('Failed to connect after multiple attempts')
      }
    }

    wsRef.current.onerror = (error) => {
      const wsUrl = getWSUrl(endpoint)
      const errorMessage = `WebSocket connection failed to ${wsUrl}`
      setError(errorMessage)
      options.onError?.(error)
      // Only log error on development, silently fail in production
      if (process.env.NODE_ENV === 'development') {
        console.warn('WebSocket connection failed - app will work without real-time updates')
      }
      
      // Don't attempt reconnection on initial failure to avoid console spam
      // WebSocket is optional - app works fine without it
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      if (wsRef.current.pingInterval) {
        clearInterval(wsRef.current.pingInterval)
      }
      wsRef.current.close()
    }
  }

  const sendMessage = (message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
    }
  }

  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [endpoint])

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    reconnect: connect,
    disconnect
  }
}

// Specific hook for configuration updates
export function useConfigUpdates(onConfigUpdate?: (configType: string, data: any) => void) {
  const [shouldConnect, setShouldConnect] = useState(true)
  const [hasAttemptedConnection, setHasAttemptedConnection] = useState(false)
  
  const wsResult = useWebSocket('/ws/config-updates', {
    onConfigUpdate,
    onConnect: () => {
      console.log('Connected to config updates')
      setShouldConnect(true)
      setHasAttemptedConnection(true)
    },
    onDisconnect: () => {
      console.log('Disconnected from config updates')
      setHasAttemptedConnection(true)
    },
    onError: (error) => {
      // Silently disable WebSocket - app works fine without it
      setShouldConnect(false)
      setHasAttemptedConnection(true)
    }
  })

  // If WebSocket fails, continue without real-time updates
  useEffect(() => {
    if (!shouldConnect && hasAttemptedConnection) {
      console.log('WebSocket not available - app will work without real-time updates')
    }
  }, [shouldConnect, hasAttemptedConnection])

  // Return connection status but don't let WebSocket failure block the app
  return {
    ...wsResult,
    isConnected: shouldConnect && wsResult.isConnected,
    error: shouldConnect ? wsResult.error : null // Clear error if we've given up connecting
  }
}