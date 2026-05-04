import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// ========== 门店 ==========
export const getStores = () => api.get('/stores')
export const getStore = (id) => api.get(`/stores/${id}`)
export const createStore = (data) => api.post('/stores', data)
export const updateStore = (id, data) => api.put(`/stores/${id}`, data)

// ========== 健康度 ==========
export const getDashboard = (storeId) => api.get(`/health/dashboard/${storeId}`)
export const submitIndicators = (data) => api.post('/health/indicators', data)
export const getIndicatorHistory = (storeId, days = 30) => api.get(`/health/history/${storeId}?days=${days}`)

// ========== 预警 ==========
export const getAlerts = (params) => api.get('/alerts', { params })
export const resolveAlert = (id, data) => api.put(`/alerts/${id}/resolve`, data)

// ========== 诊断 ==========
export const calcBreakeven = (data) => api.post('/diagnosis/breakeven', data)
export const fiveWhyAnalysis = (data) => api.post('/diagnosis/five-why', data)
export const efficiencyMatrix = (data) => api.post('/diagnosis/efficiency-matrix', data)
export const getFiveWhyIndicators = () => api.get('/diagnosis/five-why/indicators')
export const getBizTypes = () => api.get('/biz-types')

export default api
