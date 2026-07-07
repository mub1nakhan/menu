'use client'
import { useQuery } from '@tanstack/react-query'
import { CreditCard, CircleDollarSign, BadgeCheck } from 'lucide-react'
import PageHeader from '@/components/ui/page-header'
import StatCard from '@/components/ui/stat-card'
import Table from '@/components/ui/table'
import { paymentsApi } from '@/lib/api'

type PaymentRow = {
  amount?: number | string
  status?: string
  method?: string
}

export default function PaymentsPage() {
  const { data: res, isLoading } = useQuery({ queryKey: ['payments', 'list'], queryFn: () => paymentsApi.list() })
  const payments = (res?.data ?? []) as PaymentRow[]

  const total = payments.reduce((sum: number, item: PaymentRow) => sum + Number(item.amount ?? 0), 0)
  const success = payments.filter((item: PaymentRow) => item.status === 'succeeded').length

  const columns = [
    { key: 'id', title: 'ID' },
    { key: 'amount', title: 'Summa', render: (r: PaymentRow) => `₸ ${r.amount ?? 0}` },
    { key: 'status', title: 'Holat', render: (r: PaymentRow) => r.status || 'pending' },
    { key: 'method', title: 'To‘lov turi', render: (r: PaymentRow) => r.method || '—' },
  ]

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="To‘lovlar" subtitle="To‘lovlar va refundlar tarixi" />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Jami summa" value={`₸ ${total}`} subtitle="Bugungi hisobot" icon={CircleDollarSign} />
        <StatCard title="Muvaffaqiyatli" value={String(success)} subtitle="Bajarilgan to‘lovlar" icon={BadgeCheck} />
        <StatCard title="To‘lovlar" value={String(payments.length)} subtitle="Yozuvlar soni" icon={CreditCard} />
      </div>
      <div className="glass rounded-2xl p-4 text-sm text-gray-600">
        {isLoading ? 'Yuklanmoqda...' : payments.length ? <Table columns={columns} data={payments} /> : 'Hozircha to‘lovlar yo‘q.'}
      </div>
    </div>
  )
}
