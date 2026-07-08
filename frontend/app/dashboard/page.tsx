 'use client'
import { useMemo } from 'react'
import { useAuthStore } from '@/store/auth'
import StatCard from '@/components/ui/stat-card'
import { ShoppingBag, Package, Clock3, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { ordersApi, inventoryApi, paymentsApi } from '@/lib/api'
import { translate } from '@/lib/i18n'
import { useLocaleStore } from '@/store/locale'

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
  const locale = useLocaleStore((state) => state.locale)
  const t = (key: string) => translate(key, locale)

  const { data: statsData } = useQuery<{
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
      } catch {
        return { ordersCount: 0, lowStockCount: 0, paymentsTotal: 0 }
      }
    },
    staleTime: 30_000,
  })

  const actions = useMemo(
    () => [
      { title: locale === 'en' ? 'Manage the menu' : 'Menyuni boshqarish', subtitle: locale === 'en' ? 'Items, categories, prices' : 'Taomlar, kategoriyalar, narxlar', href: '/dashboard/menu' },
      { title: locale === 'en' ? 'Review orders' : 'Buyurtmalarni tekshirish', subtitle: locale === 'en' ? 'New and ready orders' : 'Yangi va tayyor buyurtmalar', href: '/dashboard/orders' },
      { title: locale === 'en' ? 'Track stock' : 'Ombor zaxirasini kuzatish', subtitle: locale === 'en' ? 'Low stock and movement' : 'Past qoldiq va harakatlar', href: '/dashboard/inventory' },
      { title: locale === 'en' ? 'Manage branches' : 'Filiallarni boshqarish', subtitle: locale === 'en' ? 'Branches and staff' : 'Filiallar va xodimlar', href: '/dashboard/branches' },
    ],
    [locale]
  )

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <section className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-600">Dashboard</p>
              <h1 className="mt-3 text-3xl font-semibold text-gray-900 sm:text-4xl">
                {user?.restaurant_name || (locale === 'en' ? 'Restaurant' : 'Restoran')} {locale === 'en' ? 'overview' : 'boshqaruvi'}
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-600">
                {t('dashboard.subtitle')}
              </p>
            </div>
            <div className="rounded-3xl bg-slate-900 px-6 py-5 text-white shadow-lg">
              <p className="text-sm font-medium text-slate-300">Bugungi foyda taxmini</p>
              <p className="mt-2 text-2xl font-semibold">\u20B8 1,245,300</p>
              <p className="mt-1 text-sm text-slate-400">Oldingi kundan 18% ko&apos;p</p>
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
                <p className="text-sm font-semibold text-gray-900">{locale === 'en' ? 'Pending orders' : 'Kutilayotgan buyurtmalar'}</p>
                <p className="mt-1 text-sm text-gray-500">{locale === 'en' ? 'The newest orders and their current status.' : 'Eng yangi buyurtmalar va ularning holati.'}</p>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">24 {locale === 'en' ? 'items' : 'ta'}</span>
            </div>
            <div className="space-y-4">
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1425 — Pizza + salad</p>
                <p className="mt-1 text-sm text-gray-500">{locale === 'en' ? 'New, 8 minutes ago' : 'Yangi, 8 daqiqa oldin'}</p>
              </div>
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1419 — Lavash + drink</p>
                <p className="mt-1 text-sm text-gray-500">{locale === 'en' ? 'Preparing, 11 minutes' : 'Tayyorlanmoqda, 11 daqiqa'}</p>
              </div>
              <div className="rounded-3xl bg-slate-900/5 p-4">
                <p className="text-sm font-medium text-gray-900">#1415 — Burger + fries</p>
                <p className="mt-1 text-sm text-gray-500">{locale === 'en' ? 'Ready for delivery' : 'Yetkazishga tayyor'}</p>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-semibold text-gray-900">{t('dashboard.quickActions')}</p>
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
              <p className="text-sm font-semibold text-gray-900">{locale === 'en' ? 'Payment and branch metrics' : 'To\'lov va filial ko\'rsatkichlari'}</p>
              <p className="mt-1 text-sm text-gray-500">{locale === 'en' ? 'The latest trends and branch activity.' : 'Eng so\'nggi trendlar va filial ishlashi.'}</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">{t('dashboard.payments')}</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">\u20B8 4,980,000</p>
              <p className="mt-2 text-sm text-gray-500">Ushbu hafta</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">{locale === 'en' ? 'Active branches' : 'Ishlovchi filiallar'}</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">6</p>
              <p className="mt-2 text-sm text-gray-500">Faol filiallar soni</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">{locale === 'en' ? 'Average order' : 'O\'rtacha buyurtma'}</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">\u20B8 48,200</p>
              <p className="mt-2 text-sm text-gray-500">So&apos;nggi 24 soat</p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-slate-50 p-5">
              <p className="text-sm text-gray-500">{locale === 'en' ? 'Menu availability' : 'Menyu mavjudligi'}</p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">78%</p>
              <p className="mt-2 text-sm text-gray-500">Aktiv mahsulotlar</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
