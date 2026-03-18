'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { productService } from '@/services/productService'
import { Product } from '@/types'

export default function ManageProductsPage() {
    const router = useRouter()
    const [products, setProducts]   = useState<Product[]>([])
    const [loading, setLoading]     = useState(true)
    const [showForm, setShowForm]   = useState(false)
    const [editingProduct, setEditingProduct] = useState<Product | null>(null)

    const fetchProducts = async () => {
        try {
            const data = await productService.getMyProducts()
            setProducts(data)
        } catch (err: any) {
            if (err.response?.status === 401) router.push('/login')
            if (err.response?.status === 403) router.push('/shops')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchProducts() }, [])

    const handleEdit = (product: Product) => {
        setEditingProduct(product)
        setShowForm(true)
    }

    const handleToggleAvailability = async (product: Product) => {
        try {
            await productService.updateProduct(product.id, {
                is_available: !product.is_available
            })
            await fetchProducts()
        } catch (err) {
            console.error(err)
        }
    }

    const handleFormClose = () => {
        setShowForm(false)
        setEditingProduct(null)
        fetchProducts()
    }

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-4 py-6">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-xl font-bold text-gray-900">My Products</h1>
                    <button
                        onClick={() => { setEditingProduct(null); setShowForm(true) }}
                        className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                    >
                        + Add product
                    </button>
                </div>

                {showForm && (
                    <ProductForm
                        product={editingProduct}
                        onClose={handleFormClose}
                    />
                )}

                {products.length === 0 && !showForm ? (
                    <div className="text-center py-16 text-gray-400">
                        <p className="mb-4">No products yet.</p>
                        <button
                            onClick={() => setShowForm(true)}
                            className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-6 py-2.5 rounded-lg"
                        >
                            Add your first product
                        </button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {products.map((product) => (
                            <div key={product.id} className="bg-white rounded-xl border border-gray-200 p-4">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium text-gray-900">{product.name}</p>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${product.is_available ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
                                                {product.is_available ? 'Available' : 'Unavailable'}
                                            </span>
                                        </div>
                                        <p className="text-sm text-green-700 font-medium mt-0.5">Rs.{product.effective_price}/{product.unit}</p>
                                        <p className="text-xs text-gray-500 mt-0.5">Stock: {product.stock_quantity} {product.unit}</p>
                                        {product.cut_types.length > 0 && (
                                            <p className="text-xs text-gray-400 mt-0.5">
                                                Cuts: {product.cut_types.map(c => c.name).join(', ')}
                                            </p>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => handleToggleAvailability(product)}
                                            className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg transition-colors"
                                        >
                                            {product.is_available ? 'Mark unavailable' : 'Mark available'}
                                        </button>
                                        <button
                                            onClick={() => handleEdit(product)}
                                            className="text-xs text-green-600 hover:text-green-700 border border-green-200 px-3 py-1.5 rounded-lg transition-colors"
                                        >
                                            Edit
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}


interface ProductFormProps {
    product: Product | null
    onClose: () => void
}

function ProductForm({ product, onClose }: ProductFormProps) {
    const [form, setForm] = useState({
        name:           product?.name || '',
        price:          product?.price || '',
        discount_price: product?.discount_price || '',
        stock_quantity: product?.stock_quantity || '',
        unit:           product?.unit || 'kg',
        description:    product?.description || '',
        is_available:   product?.is_available ?? true,
    })
    const [loading, setLoading] = useState(false)
    const [error, setError]     = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const payload = {
                name:           form.name,
                price:          form.price,
                discount_price: form.discount_price || null,
                stock_quantity: form.stock_quantity,
                unit:           form.unit,
                description:    form.description,
                is_available:   form.is_available,
            }
            if (product) {
                await productService.updateProduct(product.id, payload)
            } else {
                await productService.createProduct(payload)
            }
            onClose()
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save product.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-900">
                    {product ? 'Edit product' : 'Add new product'}
                </h2>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">Cancel</button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Product name</label>
                    <input
                        type="text"
                        value={form.name}
                        onChange={(e) => setForm({ ...form, name: e.target.value })}
                        placeholder="e.g. Fresh Whole Chicken"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Price (Rs.)</label>
                        <input
                            type="number"
                            value={form.price}
                            onChange={(e) => setForm({ ...form, price: e.target.value })}
                            placeholder="350"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Discount price (optional)</label>
                        <input
                            type="number"
                            value={form.discount_price}
                            onChange={(e) => setForm({ ...form, discount_price: e.target.value })}
                            placeholder="300"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Stock quantity</label>
                        <input
                            type="number"
                            value={form.stock_quantity}
                            onChange={(e) => setForm({ ...form, stock_quantity: e.target.value })}
                            placeholder="20"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                        <select
                            value={form.unit}
                            onChange={(e) => setForm({ ...form, unit: e.target.value })}
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="kg">Kilogram (kg)</option>
                            <option value="piece">Piece</option>
                            <option value="pack">Pack</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description (optional)</label>
                    <input
                        type="text"
                        value={form.description}
                        onChange={(e) => setForm({ ...form, description: e.target.value })}
                        placeholder="Fresh chicken from local farm"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        id="available"
                        checked={form.is_available}
                        onChange={(e) => setForm({ ...form, is_available: e.target.checked })}
                        className="text-green-600"
                    />
                    <label htmlFor="available" className="text-sm text-gray-700">Available for ordering</label>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
                >
                    {loading ? 'Saving...' : (product ? 'Update product' : 'Add product')}
                </button>
            </form>
        </div>
    )
}