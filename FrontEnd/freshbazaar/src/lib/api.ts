import axios, { type InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
    headers: {
        'Content-Type': 'application/json',
    },
})

let isRefreshing = false
let failedQueue: Array<{
    resolve: (value?: unknown) => void
    reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error)
        } else {
            prom.resolve(token)
        }
    })
    failedQueue = []
}

api.interceptors.request.use((config) => {
    const token = Cookies.get('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        if (error.response?.status !== 401) {
            return Promise.reject(error)
        }

        // Don't retry refresh endpoint — avoid infinite loop
        if (originalRequest.url?.includes('/token/refresh/')) {
            Cookies.remove('access_token')
            Cookies.remove('refresh_token')
            if (typeof window !== 'undefined') window.location.href = '/login'
            return Promise.reject(error)
        }

        const refreshToken = Cookies.get('refresh_token')
        if (!refreshToken) {
            Cookies.remove('access_token')
            Cookies.remove('refresh_token')
            if (typeof window !== 'undefined') window.location.href = '/login'
            return Promise.reject(error)
        }

        if (originalRequest._retry) {
            // Already tried refresh and failed
            Cookies.remove('access_token')
            Cookies.remove('refresh_token')
            if (typeof window !== 'undefined') window.location.href = '/login'
            return Promise.reject(error)
        }

        if (isRefreshing) {
            // Wait for the in-flight refresh to complete
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject })
            })
                .then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    return api(originalRequest)
                })
                .catch((err) => Promise.reject(err))
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
            const { data } = await axios.post(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/auth/token/refresh/`,
                { refresh: refreshToken }
            )
            const { access } = data
            Cookies.set('access_token', access, { expires: 1, sameSite: 'lax' })
            processQueue(null, access)
            originalRequest.headers.Authorization = `Bearer ${access}`
            return api(originalRequest)
        } catch (refreshError) {
            processQueue(refreshError as Error, null)
            Cookies.remove('access_token')
            Cookies.remove('refresh_token')
            if (typeof window !== 'undefined') window.location.href = '/login'
            return Promise.reject(refreshError)
        } finally {
            isRefreshing = false
        }
    }
)

export default api
