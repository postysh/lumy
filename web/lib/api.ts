import axios from 'axios'

// Use Vercel API endpoints (relative URLs work in production)
const API_BASE_URL = '/api'
const DEVICE_ID = 'lumy-001'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API Methods
export const apiClient = {
  // Status
  getStatus: async () => {
    const { data } = await api.get(`/devices/${DEVICE_ID}/status`)
    return data
  },

  // Display
  refreshDisplay: async () => {
    const { data } = await api.post('/display/refresh')
    return data
  },

  clearDisplay: async () => {
    const { data } = await api.post('/display/clear')
    return data
  },

  // Widgets
  getWidgets: async () => {
    const { data } = await api.get('/widgets')
    return data
  },

  updateWidget: async (widgetId: string, widgetData: any) => {
    const { data } = await api.post(`/widgets/${widgetId}/update`, widgetData)
    return data
  },

  triggerWidget: async (widgetId: string, widgetData: any) => {
    const { data } = await api.post(`/widgets/${widgetId}/trigger`, widgetData)
    return data
  },

  // Config
  getConfig: async () => {
    const { data } = await api.get('/config')
    return data
  },

  updateConfig: async (config: any) => {
    const { data } = await api.post('/config', config)
    return data
  },
}

// WebSocket connection
export const createWebSocket = (onMessage: (data: any) => void) => {
  const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws'
  const ws = new WebSocket(wsUrl)

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  return ws
}
