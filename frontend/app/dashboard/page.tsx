 'use client'
import { useMemo } from 'react'
import { useAuthStore } from '@/store/auth'
import StatCard from '@/components/ui/stat-card'
import { ShoppingBag, Package, CreditCard, Clock3, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { ordersApi, inventoryApi, paymentsApi } from '@/lib/api'

const STATS = [
  {
    title: 'Bugungi savdo',
    value: '\u20B8 1,245,300',
    subtitle: 'Haftalik o\'sish +18%',
    icon: TrendingUp,
    delta: '+18.0%',
  },
  {
    title: 'Yangi buyurtmalar',
    value: '58',
    subtitle: '24 soatda',
    icon: ShoppingBag,
    delta: '+12%',
  },
  {
    title: 'Past qoldiqdagi mahsulotlar',
    value: '7 ta',
    subtitle: 'Ombor ogohlantirishlari',
    icon: Package,
    delta: '+2 ta',
  },
  {
    title: 'Oxirgi buyurtma vaqti',
    value: '12 min',
    subtitle: 'Yaqinda qabul qilingan',
    icon: Clock3,
    delta: '+4 min',
  },
]

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)

  const { data: statsData, isLoading } = useQuery<{
    ordersCount: number
    lowStockCount: number
    paymentsTotal: number
  }>({
    queryKey: ['dashboard', 'stats'],
    queryFn: async () => {
      try {
        const [ordersRes, lowStockRes, paymentsRes] = await Promise.all([
          ordersApi.orders.list(),
          inventoryApi.stock.lowStock(),
          paymentsApi.list(),
        ])

        const ordersCount = ordersRes?.data?.length ?? 0
        const lowStockCount = lowStockRes?.data?.length ?? 0
        const paymentsTotal = paymentsRes?.data?.total ?? paymentsRes?.data?.sum ?? 0

        return { ordersCount, lowStockCount, paymentsTotal }
      } catch (err) {
        return { ordersCount: 0, lowStockCount: 0, paymentsTotal: 0 }
      }
    },
    staleTime: 30_000,
  })

  const actions = useMemo(
    () => [
      { title: 'Menyuni boshqarish', subtitle: 'Taomlar, kategoriyalar, narxlar', href: '/dashboard/menu' },
      { title: 'Buyurtmalarni tekshirish', subtitle: 'Yangi va tayyor buyurtmalar', href: '/dashboard/orders' },
      { title: 'Ombor zaxirasini kuzatish', subtitle: 'Past qoldiq va harakatlar', href: '/dashboard/inventory' },
      { title: 'Filiallarni boshqarish', subtitle: 'Filiallar va xodimlar', href: '/dashboard/branches' },
    ],
    []
  )

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <section className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-600">Dashboard</p>
              <h1 className="mt-3 text-3xl font-semibold text-gray-900 sm:text-4xl">
                {user?.restaurant_name || 'Restoran'} boshqaruvi
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-600">
                Eng muhim ko'rsatkichlarni shu yerdan kuzatib boring: buyurtmalar, ombor, to'lovlar va filiallar.
              </p>
            </div>
            <div className="rounded-3xl bg-slate-900 px-6 py-5 text-white shadow-lg">
              <p className="text-sm font-medium text-slate-300">Bugungi foyda taxmini</p>
              <p className="mt-2 text-2xl font-semibold">\u20B8 1,245,300</p>
              <p className="mt-1 text-sm text-slate-400">Oldingi kundan 18% ko'p</p>
            </div>
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-4 lg:grid-cols-2">
          {STATS.map((item) => {
            let value = item.value
            if (statsData) {
              if (item.title === 'Bugungi savdo') value = `\u20B8 ${Number(statsData.paymentsTotal ?? 0).toLocaleString()}`
              if (item.title === 'Yangi buyurtmalar') value = String(statsData.ordersCount ?? 0)
              if (item.title === 'Past qoldiqdagi mahsulotlar') value = `${statsData.lowStockCount ?? 0} ta`
            }

            return <StatCard key={item.title} {...item} value={value} />
          })}
        </section>

        <div className="grid gap-5 lg:grid-cols-3">
          <section className="lg:col-span-2 rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-900">Kutilayotgan buyurtmalar</p>
                <p className="mt-1 text-sm text-gray-500">Eng yangi buyurtmalar va ularning holati.</p>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">24 ta</span>
            </div>
            <div className="space-y-4">
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1425 — Pizza + salat</p>
                <p className="mt-1 text-sm text-gray-500">Yangi, 8 daqiqa oldin</p>
              </div>
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1419 — Lavash + ichimlik</p>
                <p className="mt-1 text-sm text-gray-500">Tayyorlanmoqda, 11 daqiqa</p>
              </div>
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1415 — Burger + kartoshka</p>
                <p className="mt-1 text-sm text-gray-500">Yetkazishga tayyor</p>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-semibold text-gray-900">Tezkor harakatlar</p>
            <div className="mt-5 space-y-3">
              {actions.map((action) => (
                <a
                  key={action.title}
                  href={action.href}
                  className="block rounded-3xl border border-gray-200 bg-slate-50 px-4 py-4 text-sm text-gray-700 transition hover:border-slate-300 hover:bg-slate-100"
                >
                  <p className="font-medium">{action.title}</p>
                  <p className="mt-1 text-sm text-gray-500">{action.subtitle}</p>
                </a>
              ))}
            </div>
          </section>
        </div>

        <section className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-900">To'lov va filial ko'rsatkichlari</p>
              <p className="mt-1 text-sm text-gray-500">Eng so'nggi trendlar va filial ishlashi.</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">To'lovlar</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">\u20B8 4,980,000</p>
              <p className="mt-2 text-sm text-gray-500">Ushbu hafta</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">Ishlovchi filiallar</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">6</p>
              <p className="mt-2 text-sm text-gray-500">Faol filiallar soni</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">O'rtacha buyurtma</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">\u20B8 48,200</p>
              <p className="mt-2 text-sm text-gray-500">So'nggi 24 soat</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">Menyu mavjudligi</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">78%</p>
              <p className="mt-2 text-sm text-gray-500">Aktiv mahsulotlar</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
