'use client'
import { useQuery } from '@tanstack/react-query'
import { GitBranch, Building2, Users } from 'lucide-react'
import PageHeader from '@/components/ui/page-header'
import StatCard from '@/components/ui/stat-card'
import Table from '@/components/ui/table'
import { branchApi } from '@/lib/api'

type BranchRow = {
  name?: string
  address?: string
  phone?: string
}

export default function BranchesPage() {
  const { data: res, isLoading } = useQuery({ queryKey: ['branches', 'list'], queryFn: () => branchApi.list() })
  const branches = (res?.data ?? []) as BranchRow[]

  const columns = [
    { key: 'name', title: 'Filial nomi' },
    { key: 'address', title: 'Manzil', render: (r: BranchRow) => r.address || '—' },
    { key: 'phone', title: 'Telefon', render: (r: BranchRow) => r.phone || '—' },
  ]

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Filiallar" subtitle="Filiallar va joylashuvlar" />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Jami filiallar" value={String(branches.length)} subtitle="Faol filiallar" icon={GitBranch} />
        <StatCard title="Ofis joylari" value={String(branches.length)} subtitle="Joylashtirish" icon={Building2} />
        <StatCard title="Xodimlar" value="—" subtitle="Tez orada" icon={Users} />
      </div>
      <div className="glass rounded-2xl p-4 text-sm text-gray-600">
        {isLoading ? 'Yuklanmoqda...' : branches.length ? <Table columns={columns} data={branches} /> : 'Hozircha filiallar yo‘q.'}
      </div>
    </div>
  )
}
