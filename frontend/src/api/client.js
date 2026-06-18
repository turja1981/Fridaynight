import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: attach Authorization token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('eap_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: handle 401 unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('eap_token')
      localStorage.removeItem('eap_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
