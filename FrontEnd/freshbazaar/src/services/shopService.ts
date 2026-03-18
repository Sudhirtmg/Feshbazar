import api from '@/lib/api'
import { Shop } from '@/types'

export const shopService = {
    getShops: async (city?: string): Promise<Shop[]> => {
        const params = city ? { city } : {}
        const res = await api.get('/api/shops/', { params })
        return res.data
    },

    getShop: async (slug: string): Promise<Shop> => {
        const res = await api.get(`/api/shops/${slug}/`)
        return res.data
    },

    getMyShop: async (): Promise<Shop> => {
        const res = await api.get('/api/shops/my-shop/')
        return res.data
    },

    updateMyShop: async (slug: string, data: Partial<Shop>): Promise<Shop> => {
        const res = await api.patch(`/api/shops/${slug}/update/`, data)
        return res.data
    },

    createShop: async (data: {
        name: string
        phone: string
        address: string
        city: string
        description?: string
    }): Promise<Shop> => {
        const res = await api.post('/api/shops/create/', data)
        return res.data
    },
}