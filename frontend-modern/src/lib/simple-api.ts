// Simple fetch-based API client using Next.js API proxy
export const simpleApi = {
  async getScenarios() {
    console.log('SimpleApi: Fetching scenarios via Next.js API proxy')
    
    try {
      const response = await fetch('/api/scenarios', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      console.log('SimpleApi: Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('SimpleApi: Success! Got', data.length, 'scenarios')
      return data
      
    } catch (error) {
      console.error('SimpleApi: Error fetching scenarios:', error)
      throw error
    }
  }
}