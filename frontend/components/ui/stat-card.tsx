import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string
  subtitle?: string
  icon: LucideIcon
  delta?: string
}

export default function StatCard({ title, value, subtitle, icon: Icon, delta }: StatCardProps) {
  return (
    <div className="rounded-3xl glass p-5 transition hover:shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-gray-900">{value}</p>
          {subtitle ? <p className="mt-2 text-sm text-gray-500">{subtitle}</p> : null}
        </div>
        <div className="rounded-2xl bg-white/30 p-3 text-gray-700 backdrop-blur-sm">
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {delta ? (
        <div className="mt-4 flex items-center gap-2 text-sm text-emerald-600">
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">↑</span>
          {delta}
        </div>
      ) : null}
    </div>
  )
}
