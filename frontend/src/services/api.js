import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let authToken = null

// Initialize token from localStorage if available
if (typeof window !== 'undefined') {
  authToken = localStorage.getItem('token')
  if (authToken) {
    api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
  }
}

api.setToken = (token) => {
  authToken = token
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
let isRedirecting = false

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - prevent infinite redirect loops
      if (typeof window !== 'undefined' && !isRedirecting) {
        isRedirecting = true
        localStorage.removeItem('token')
        authToken = null
        delete api.defaults.headers.common['Authorization']
        // Only redirect if not already on login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        } else {
          isRedirecting = false
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api


