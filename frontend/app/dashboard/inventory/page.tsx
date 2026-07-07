'use client'
import { useQuery } from '@tanstack/react-query'
import { Package, AlertTriangle, TrendingUp } from 'lucide-react'
import PageHeader from '@/components/ui/page-header'
import StatCard from '@/components/ui/stat-card'
import Table from '@/components/ui/table'
import { inventoryApi } from '@/lib/api'

type InventoryItem = {
  ingredient?: { name?: string }
  name?: string
  stock?: number | string
  min_stock?: number | string
  unit?: string
}

export default function InventoryPage() {
  const { data: res, isLoading } = useQuery({ queryKey: ['inventory', 'stock'], queryFn: () => inventoryApi.stock.list() })
  const stock = (res?.data ?? []) as InventoryItem[]
  const low = stock.filter((item: InventoryItem) => Number(item.stock) <= Number(item.min_stock ?? 0)).length

  const columns = [
    { key: 'ingredient', title: 'Ingredient', render: (r: InventoryItem) => r.ingredient?.name || r.name || '—' },
    { key: 'stock', title: 'Qoldiq', render: (r: InventoryItem) => `${r.stock ?? 0}` },
    { key: 'unit', title: 'Birlik', render: (r: InventoryItem) => r.unit || '—' },
    { key: 'status', title: 'Holat', render: (r: InventoryItem) => Number(r.stock) <= Number(r.min_stock ?? 0) ? 'Past' : 'Yaxshi' },
  ]

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Ombor" subtitle="Maxsulotlar va ingredientlar qoldig‘i" />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Jami punktlar" value={String(stock.length)} subtitle="Qoldiq yozuvlari" icon={Package} />
        <StatCard title="Past qoldiq" value={String(low)} subtitle="Yangilanish kerak" icon={AlertTriangle} />
        <StatCard title="Tezkor ko‘rish" value="Live" subtitle="Ombor holati" icon={TrendingUp} />
      </div>
      <div className="glass rounded-2xl p-4 text-sm text-gray-600">
        {isLoading ? 'Yuklanmoqda...' : stock.length ? <Table columns={columns} data={stock} /> : 'Hozircha ombor ma’lumotlari yo‘q.'}
      </div>
    </div>
  )
}
