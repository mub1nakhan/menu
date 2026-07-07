'use client'
import { useQuery } from '@tanstack/react-query'
import { ShoppingBag, Clock3, CheckCircle2 } from 'lucide-react'
import PageHeader from '@/components/ui/page-header'
import StatCard from '@/components/ui/stat-card'
import Table from '@/components/ui/table'
import { ordersApi } from '@/lib/api'

type OrderRow = {
  id?: string
  customer_name?: string
  total?: number | string
  status?: string
  created_at?: string
}

export default function OrdersPage() {
  const { data: res, isLoading } = useQuery({ queryKey: ['orders', 'list'], queryFn: () => ordersApi.orders.list() })
  const orders = (res?.data ?? []) as OrderRow[]

  const pending = orders.filter((o: OrderRow) => o.status === 'pending').length
  const ready = orders.filter((o: OrderRow) => o.status === 'ready').length
  const served = orders.filter((o: OrderRow) => o.status === 'served').length

  const columns = [
    { key: 'id', title: 'ID' },
    { key: 'customer_name', title: 'Mijoz', render: (r: OrderRow) => r.customer_name || '—' },
    { key: 'total', title: 'Jami', render: (r: OrderRow) => `₸ ${r.total ?? 0}` },
    { key: 'status', title: 'Holat', render: (r: OrderRow) => r.status || 'pending' },
    { key: 'created_at', title: 'Vaqt', render: (r: OrderRow) => r.created_at || '—' },
  ]

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Buyurtmalar" subtitle="Real-time buyurtmalarni kuzatish" />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Jarayonda" value={String(pending)} subtitle="Yangi buyurtmalar" icon={Clock3} />
        <StatCard title="Tayyor" value={String(ready)} subtitle="Tayyor bo‘lishi kerak" icon={CheckCircle2} />
        <StatCard title="Yetkazilgan" value={String(served)} subtitle="Yopiq buyurtmalar" icon={ShoppingBag} />
      </div>
      <div className="glass rounded-2xl p-4 text-sm text-gray-600">
        {isLoading ? 'Yuklanmoqda...' : orders.length ? <Table columns={columns} data={orders} /> : 'Hozircha buyurtmalar yo‘q.'}
      </div>
    </div>
  )
}
