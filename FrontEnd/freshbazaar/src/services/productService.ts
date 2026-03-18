// src/services/productService.ts
import api from '@/lib/api'
import { Product } from '@/types'

interface ProductFilters {
    shop?: number
    category?: string
    city?: string
}

interface ProductPayload {
    name?: string
    price?: string | number
    discount_price?: string | number | null
    stock_quantity?: string | number
    unit?: string
    description?: string
    is_available?: boolean
}

export const productService = {
    getProducts: async (filters?: ProductFilters): Promise<Product[]> => {
        const res = await api.get('/api/products/', { params: filters })
        return res.data
    },

    getProduct: async (id: number): Promise<Product> => {
        const res = await api.get(`/api/products/${id}/`)
        return res.data
    },

    getMyProducts: async (): Promise<Product[]> => {
        const res = await api.get('/api/products/my-products/')
        return res.data
    },

    createProduct: async (data: ProductPayload): Promise<Product> => {
        const res = await api.post('/api/products/create/', data)
        return res.data
    },

    updateProduct: async (id: number, data: ProductPayload): Promise<Product> => {
        const res = await api.patch(`/api/products/${id}/update/`, data)
        return res.data
    },
}