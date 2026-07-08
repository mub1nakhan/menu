'use client'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'
import { authApi } from '@/lib/api'
import {
  LayoutDashboard, UtensilsCrossed, ShoppingBag,
  Package, CreditCard, GitBranch, LogOut, ChefHat, User, Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from '@/lib/toast'
import { LocaleSwitcher } from '@/components/locale-switcher'
import { translate } from '@/lib/i18n'
import { useLocaleStore } from '@/store/locale'

const NAV_BASE = [
  { href: '/dashboard',           icon: LayoutDashboard, label: "Bosh sahifa" },
  { href: '/dashboard/menu',      icon: UtensilsCrossed, label: "Menyu" },
  { href: '/dashboard/orders',    icon: ShoppingBag,     label: "Buyurtmalar" },
  { href: '/dashboard/inventory', icon: Package,         label: "Ombor" },
  { href: '/dashboard/payments',  icon: CreditCard,      label: "To'lovlar" },
  { href: '/dashboard/branches',  icon: GitBranch,       label: "Filiallar" },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, setUser, logout, role } = useAuthStore()
  const locale = useLocaleStore((state) => state.locale)
  const t = (key: string) => translate(key, locale)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }
    if (!user) {
      authApi.me()
        .then((res) => setUser(res.data))
        .catch(() => { router.push('/login') })
    }
  }, [router, setUser, user])

  useEffect(() => {
    setMobileOpen(false)
  }, [pathname])

  const normalizedRole = (role || user?.role_code || user?.role || '').toLowerCase()
  const isChefRole = ['chef', 'manager', 'owner', 'super admin', 'super_admin'].includes(normalizedRole)

  useEffect(() => {
    if (!user) return
    if (pathname === '/dashboard' && isChefRole) {
      router.replace('/dashboard/chef')
      return
    }
    if (pathname === '/dashboard/chef' && !isChefRole) {
      router.replace('/dashboard')
    }
  }, [isChefRole, pathname, router, user])

  const handleLogout = () => {
    logout()
    toast.success(locale === 'en' ? 'Signed out' : 'Tizimdan chiqildi')
    router.push('/login')
  }

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: t('dashboard.home') },
    { href: '/dashboard/menu', icon: UtensilsCrossed, label: t('dashboard.menu') },
    { href: '/dashboard/orders', icon: ShoppingBag, label: t('dashboard.orders') },
    { href: '/dashboard/inventory', icon: Package, label: t('dashboard.inventory') },
    { href: '/dashboard/payments', icon: CreditCard, label: t('dashboard.payments') },
    { href: '/dashboard/branches', icon: GitBranch, label: t('dashboard.branches') },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <button
        type="button"
        onClick={() => setMobileOpen(true)}
        className="fixed left-4 top-4 z-40 rounded-full border border-gray-200 bg-white/90 p-2 text-gray-700 shadow-sm md:hidden"
        aria-label="Open navigation"
      >
        <Menu className="h-4 w-4" />
      </button>

      {mobileOpen ? (
        <button
          type="button"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-black/20 md:hidden"
          aria-label="Close navigation"
        />
      ) : null}

      <div className="flex min-h-screen">
        <aside className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-60 flex-col border-r border-gray-200 bg-white transition-transform duration-200 md:static md:translate-x-0',
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}>
          <div className="flex items-center gap-2.5 border-b border-gray-100 px-5 py-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-black">
              <ChefHat className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold leading-tight text-gray-900">Menu</p>
              <p className="text-xs text-gray-400">{user?.restaurant_name || '...'}</p>
            </div>
          </div>

          <div className="px-3 py-3">
            <LocaleSwitcher />
          </div>

          <nav className="flex-1 space-y-0.5 px-3 py-2">
            {navItems.filter(({ href }) => href !== '/dashboard/chef' || isChefRole).map(({ href, icon: Icon, label }) => {
              const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                    active ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  )}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  {label}
                </Link>
              )
            })}
          </nav>

          <div className="border-t border-gray-100 p-3">
            <div className="mb-1 flex items-center gap-2.5 px-2 py-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-200">
                <User className="h-3.5 w-3.5 text-gray-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-gray-900">{user?.full_name}</p>
                <p className="truncate text-xs text-gray-400">{user?.role_code || user?.role || 'User'}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900"
            >
              <LogOut className="h-4 w-4" />
              {t('dashboard.logout')}
            </button>
          </div>
        </aside>

        <main className="flex-1 overflow-auto md:ml-0">
          {children}
        </main>
      </div>
    </div>
  )
}