/**
 * Configuration for API and WebSocket connections
 */

export const API_CONFIG = {
  // API Base URL
  baseURL: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8006' 
    : process.env.NEXT_PUBLIC_API_URL || 'https://vivikafinance-api.railway.app',
  
  // WebSocket Base URL  
  wsBaseURL: process.env.NODE_ENV === 'development'
    ? 'ws://localhost:8006'
    : (process.env.NEXT_PUBLIC_API_URL || 'https://vivikafinance-api.railway.app').replace('https://', 'wss://').replace('http://', 'ws://'),
  
  // Endpoints
  endpoints: {
    health: '/api/health',
    financialConfig: '/api/financial-config',
    houseData: '/api/financial-config/house-data',
    adminHouseData: '/api/admin/financial-config/house-data',
    adminTaxRates: '/api/admin/financial-config/tax-rates',
    adminBackup: '/api/admin/financial-config/backup',
    adminExpenseCategory: '/api/admin/financial-config/expense-category',
    adminRestore: '/api/admin/financial-config/restore',
  },
  
  // WebSocket endpoints
  wsEndpoints: {
    configUpdates: '/ws/config-updates',
    simulation: '/ws/simulation'
  }
}

// Helper function to get full API URL
export const getAPIUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`
}

// Helper function to get full WebSocket URL
export const getWSUrl = (endpoint: string): string => {
  return `${API_CONFIG.wsBaseURL}${endpoint}`
}