'use client'

import { useEffect, useMemo, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChefHat, Clock3, Flame, CheckCircle2, ArrowRight, Radio } from 'lucide-react'
import Button from '@/components/ui/button'
import { ordersApi } from '@/lib/api'
import { toast } from '@/lib/toast'
import { translate } from '@/lib/i18n'
import { useLocaleStore } from '@/store/locale'

type OrderItem = {
  id?: string
  status?: string
  created_at?: string
  total_amount?: number | string
  item_count?: number
  items?: Array<{ name?: string }>
}

const STATUS_SEQUENCE = ['pending', 'preparing', 'ready', 'served']
const STATUS_LABELS: Record<string, string> = {
  pending: 'Yangi',
  preparing: 'Tayyorlanmoqda',
  ready: 'Tayyor',
  served: 'Berildi',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-700',
  preparing: 'bg-sky-100 text-sky-700',
  ready: 'bg-emerald-100 text-emerald-700',
  served: 'bg-slate-100 text-slate-700',
}

function getElapsedMinutes(createdAt?: string) {
  if (!createdAt) return 0
  const created = new Date(createdAt)
  if (Number.isNaN(created.getTime())) return 0
  return Math.max(0, Math.floor((Date.now() - created.getTime()) / 60000))
}

export default function ChefPage() {
  const locale = useLocaleStore((state) => state.locale)
  const t = (key: string) => translate(key, locale)
  const seenOrderIds = useRef<Set<string>>(new Set())

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['chef-orders'],
    queryFn: async () => {
      const response = await ordersApi.orders.list()
      return (response.data || []) as OrderItem[]
    },
    refetchInterval: 5000,
  })

  useEffect(() => {
    const poll = async () => {
      try {
        const response = await ordersApi.orders.list()
        const orders = (response.data || []) as OrderItem[]
        const pending = orders.filter((order) => (order.status || 'pending') === 'pending')
        const newIds = pending.map((order) => String(order.id)).filter((id) => !seenOrderIds.current.has(id))
        if (newIds.length > 0) {
          seenOrderIds.current = new Set([...seenOrderIds.current, ...newIds])
          if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(locale === 'en' ? 'New order received' : 'Yangi buyurtma keldi', { body: `${newIds.length} ${locale === 'en' ? 'new kitchen order' : 'yangi oshxona buyurtmasi'}` })
          }
          toast.success(locale === 'en' ? 'New order received' : 'Yangi buyurtma keldi')
        }
      } catch {
        // Keep the kitchen screen resilient if polling fails.
      }
    }

    poll()
    const interval = window.setInterval(poll, 5000)
    return () => window.clearInterval(interval)
  }, [locale])

  const orders = useMemo(() => data || [], [data])
  const activeOrders = orders.filter((order) => STATUS_SEQUENCE.includes(order.status || ''))
  const pending = activeOrders.filter((order) => order.status === 'pending')
  const preparing = activeOrders.filter((order) => order.status === 'preparing')
  const ready = activeOrders.filter((order) => order.status === 'ready')

  async function advanceStatus(order: OrderItem) {
    const currentStatus = order.status || 'pending'
    const nextIndex = STATUS_SEQUENCE.indexOf(currentStatus) + 1
    const nextStatus = STATUS_SEQUENCE[nextIndex] || 'served'

    try {
      await ordersApi.orders.updateStatus(String(order.id), { status: nextStatus })
      toast.success(locale === 'en' ? 'Order moved forward' : `Buyurtma ${STATUS_LABELS[nextStatus]} holatiga o'zgartirildi`)
      refetch()
    } catch {
      toast.error(locale === 'en' ? 'Could not update the order' : 'Holatni yangilab bo\'lmadi')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6 lg:p-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <div className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="mb-3 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white">
                <ChefHat className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-semibold text-slate-900">{t('chef.title')}</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-500">
                {t('chef.description')}
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                <div className="font-semibold">{pending.length}</div>
                <div>{t('chef.new')}</div>
              </div>
              <div className="rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-700">
                <div className="font-semibold">{preparing.length}</div>
                <div>{t('chef.preparing')}</div>
              </div>
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                <div className="font-semibold">{ready.length}</div>
                <div>{t('chef.ready')}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
          <Radio className="h-4 w-4 text-emerald-500" />
          <span>{t('common.live')}</span>
        </div>

        {isLoading ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-8 text-sm text-slate-500">
            {t('common.loading')}
          </div>
        ) : activeOrders.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
            {t('chef.empty')}
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {activeOrders.map((order) => {
              const currentStatus = order.status || 'pending'
              const nextStatus = STATUS_SEQUENCE[STATUS_SEQUENCE.indexOf(currentStatus) + 1] || 'served'
              const elapsed = getElapsedMinutes(order.created_at)

              return (
                <div key={order.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{locale === 'en' ? 'Order' : 'Buyurtma'} #{String(order.id).slice(0, 6)}</p>
                      <p className="mt-1 text-xs text-slate-500">{elapsed} {locale === 'en' ? 'min ago' : 'daq. oldin'}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_COLORS[currentStatus] || STATUS_COLORS.pending}`}>
                      {STATUS_LABELS[currentStatus] || currentStatus}
                    </span>
                  </div>

                  <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
                    <Clock3 className="h-4 w-4" />
                    <span>{order.items?.length || order.item_count || 0} {locale === 'en' ? 'items' : 'ta taom'}</span>
                  </div>

                  <div className="mt-4 rounded-2xl bg-slate-50 p-3 text-sm text-slate-600">
                    {order.items?.map((item, index) => (
                      <div key={`${order.id}-${index}`} className="flex items-center justify-between py-1">
                        <span>{item.name || (locale === 'en' ? 'Dish' : 'Taom')}</span>
                        <span className="text-slate-400">•</span>
                      </div>
                    )) || <div>{locale === 'en' ? 'Order details will appear here.' : 'Buyurtma tafsilotlari ko\'rsatilmoqda.'}</div>}
                  </div>

                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm text-slate-500">
                      {locale === 'en' ? 'Total' : 'Jami'}: <span className="font-semibold text-slate-900">{Number(order.total_amount || 0).toLocaleString()} {locale === 'en' ? 'sum' : 'so\'m'}</span>
                    </div>
                    <Button onClick={() => advanceStatus(order)} className="gap-2">
                      {currentStatus === 'served' ? <CheckCircle2 className="h-4 w-4" /> : <Flame className="h-4 w-4" />}
                      {currentStatus === 'served' ? (locale === 'en' ? 'Done' : 'Tugallangan') : `${STATUS_LABELS[nextStatus] || (locale === 'en' ? 'Next' : 'Keyingi')} ${locale === 'en' ? 'step' : 'holat'}`}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
