'use client'
import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'
import { authApi } from '@/lib/api'
import {
  LayoutDashboard, UtensilsCrossed, ShoppingBag,
  Package, CreditCard, GitBranch, LogOut, ChefHat, User
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

const NAV = [
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
  const { user, setUser, logout, isAuthenticated } = useAuthStore()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    if (!user) {
      authApi.me()
        .then(res => setUser(res.data))
        .catch(() => { router.push('/login') })
    }
  }, [])

  const handleLogout = () => {
    logout()
    toast.success("Tizimdan chiqildi")
    router.push('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-gray-100">
          <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
            <ChefHat className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 leading-tight">Menu</p>
            <p className="text-xs text-gray-400">{user?.restaurant_name || '...'}</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV.map(({ href, icon: Icon, label }) => {
            const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  active
                    ? "bg-gray-900 text-white"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        <div className="border-t border-gray-100 p-3">
          <div className="flex items-center gap-2.5 px-2 py-2 mb-1">
            <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-gray-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400 truncate">{user?.role_code}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-900 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Chiqish
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}