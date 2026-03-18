'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { shopService } from '@/services/shopService'
import { Shop } from '@/types'

export default function ShopSettingsPage() {
    const router = useRouter()
    const [shop, setShop]       = useState<Shop | null>(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving]   = useState(false)
    const [saved, setSaved]     = useState(false)
    const [error, setError]     = useState('')

    const [form, setForm] = useState({
        name:            '',
        phone:           '',
        address:         '',
        city:            '',
        description:     '',
        is_open:         true,
        has_delivery:    true,
        has_pickup:      true,
        delivery_charge: '',
    })

    useEffect(() => {
        const fetchShop = async () => {
            try {
                const data = await shopService.getMyShop()
                setShop(data)
                setForm({
                    name:            data.name,
                    phone:           data.phone,
                    address:         data.address,
                    city:            data.city,
                    description:     data.description,
                    is_open:         data.is_open,
                    has_delivery:    data.has_delivery,
                    has_pickup:      data.has_pickup,
                    delivery_charge: data.delivery_charge,
                })
            } catch (err: any) {
                if (err.response?.status === 401) router.push('/login')
            } finally {
                setLoading(false)
            }
        }
        fetchShop()
    }, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!shop) return
        setSaving(true)
        setError('')
        try {
            await shopService.updateMyShop(shop.slug, form)
            setSaved(true)
            setTimeout(() => setSaved(false), 3000)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save settings.')
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>
    if (!shop)   return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">No shop found.</div>

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-2xl mx-auto px-4 py-6">
                <h1 className="text-xl font-bold text-gray-900 mb-6">Shop Settings</h1>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>
                )}
                {saved && (
                    <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">Settings saved successfully.</div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Basic info */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h2 className="font-semibold text-gray-900 mb-4">Basic information</h2>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Shop name</label>
                                <input
                                    type="text"
                                    value={form.name}
                                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                <input
                                    type="text"
                                    value={form.phone}
                                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                                <input
                                    type="text"
                                    value={form.address}
                                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                                <input
                                    type="text"
                                    value={form.city}
                                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description (optional)</label>
                                <textarea
                                    value={form.description}
                                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                                    rows={2}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Status */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h2 className="font-semibold text-gray-900 mb-4">Shop status</h2>
                        <label className="flex items-center justify-between cursor-pointer">
                            <div>
                                <p className="text-sm font-medium text-gray-900">Shop is open</p>
                                <p className="text-xs text-gray-500">Customers can place orders</p>
                            </div>
                            <div className={`w-12 h-6 rounded-full transition-colors ${form.is_open ? 'bg-green-500' : 'bg-gray-300'}`}
                                onClick={() => setForm({ ...form, is_open: !form.is_open })}>
                                <div className={`w-5 h-5 bg-white rounded-full shadow mt-0.5 transition-transform ${form.is_open ? 'translate-x-6' : 'translate-x-0.5'}`} />
                            </div>
                        </label>
                    </div>

                    {/* Delivery settings */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h2 className="font-semibold text-gray-900 mb-4">Delivery settings</h2>
                        <div className="space-y-4">
                            <label className="flex items-center justify-between cursor-pointer">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">Offer delivery</p>
                                    <p className="text-xs text-gray-500">Deliver orders to customers</p>
                                </div>
                                <div className={`w-12 h-6 rounded-full transition-colors ${form.has_delivery ? 'bg-green-500' : 'bg-gray-300'}`}
                                    onClick={() => setForm({ ...form, has_delivery: !form.has_delivery })}>
                                    <div className={`w-5 h-5 bg-white rounded-full shadow mt-0.5 transition-transform ${form.has_delivery ? 'translate-x-6' : 'translate-x-0.5'}`} />
                                </div>
                            </label>

                            {form.has_delivery && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Delivery charge (Rs.)</label>
                                    <input
                                        type="number"
                                        value={form.delivery_charge}
                                        onChange={(e) => setForm({ ...form, delivery_charge: e.target.value })}
                                        placeholder="50"
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    />
                                </div>
                            )}

                            <label className="flex items-center justify-between cursor-pointer">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">Offer pickup</p>
                                    <p className="text-xs text-gray-500">Customers can collect from shop</p>
                                </div>
                                <div className={`w-12 h-6 rounded-full transition-colors ${form.has_pickup ? 'bg-green-500' : 'bg-gray-300'}`}
                                    onClick={() => setForm({ ...form, has_pickup: !form.has_pickup })}>
                                    <div className={`w-5 h-5 bg-white rounded-full shadow mt-0.5 transition-transform ${form.has_pickup ? 'translate-x-6' : 'translate-x-0.5'}`} />
                                </div>
                            </label>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={saving}
                        className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50"
                    >
                        {saving ? 'Saving...' : saved ? 'Saved!' : 'Save settings'}
                    </button>
                </form>
            </div>
        </div>
    )
}