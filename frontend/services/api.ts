import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Har bir so'rovga access token qo'shamiz
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 bo'lsa refresh qilamiz, bo'lmasa login'ga
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh })
          localStorage.setItem('access_token', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      } else {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── API functions ─────────────────────────────────────────────────────────────

// Auth
export const authApi = {
  login: (data: { restaurant_slug: string; email: string; password: string }) =>
    api.post('/auth/login/', data),
  me: () => api.get('/auth/me/'),
  refresh: (refresh: string) => api.post('/auth/refresh/', { refresh }),
}

// Branches
export const branchApi = {
  list: () => api.get('/branches/'),
  create: (data: object) => api.post('/branches/', data),
  update: (id: string, data: object) => api.patch(`/branches/${id}/`, data),
  remove: (id: string) => api.delete(`/branches/${id}/`),
}

// Menu
export const menuApi = {
  categories: {
    list: (params?: object) => api.get('/categories/', { params }),
    create: (data: object) => api.post('/categories/', data),
    update: (id: string, data: object) => api.patch(`/categories/${id}/`, data),
    remove: (id: string) => api.delete(`/categories/${id}/`),
  },
  products: {
    list: (params?: object) => api.get('/products/', { params }),
    create: (data: any) => {
      if (data instanceof FormData) {
        return api.post('/products/', data, { headers: { 'Content-Type': 'multipart/form-data' } })
      }
      return api.post('/products/', data)
    },
    update: (id: string, data: any) => {
      if (data instanceof FormData) {
        return api.patch(`/products/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } })
      }
      return api.patch(`/products/${id}/`, data)
    },
    remove: (id: string) => api.delete(`/products/${id}/`),
    toggleAvailability: (id: string) =>
      api.patch(`/products/${id}/toggle-availability/`),
  },
}

// Orders
export const ordersApi = {
  tables: {
    list: () => api.get('/tables/'),
    create: (data: object) => api.post('/tables/', data),
  },
  orders: {
    list: (params?: object) => api.get('/orders/', { params }),
    create: (data: object) => api.post('/orders/', data),
    updateStatus: (id: string, data: object) =>
      api.patch(`/orders/${id}/status/`, data),
  },
}

// Inventory
export const inventoryApi = {
  ingredients: {
    list: () => api.get('/inventory/ingredients/'),
    create: (data: object) => api.post('/inventory/ingredients/', data),
    update: (id: string, data: object) =>
      api.patch(`/inventory/ingredients/${id}/`, data),
  },
  stock: {
    list: () => api.get('/inventory/stock/'),
    lowStock: () => api.get('/inventory/stock/low-stock/'),
    adjust: (data: object) => api.post('/inventory/stock/adjust/', data),
  },
  movements: {
    list: () => api.get('/inventory/movements/'),
  },
}

// Payments
export const paymentsApi = {
  list: (params?: object) => api.get('/payments/', { params }),
  create: (data: object) => api.post('/payments/', data),
  refund: (id: string) => api.post(`/payments/${id}/refund/`),
}