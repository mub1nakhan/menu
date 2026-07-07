'use client'
import { useState, type FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { ChefHat } from 'lucide-react'
import Button from '@/components/ui/button'
import Input from '@/components/ui/input'
import Field from '@/components/ui/field'
import { authApi } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useAuthStore } from '@/store/auth'

export default function LoginPage() {
  const router = useRouter()
  const { setUser, setTokens } = useAuthStore()
  const [restaurantSlug, setRestaurantSlug] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!restaurantSlug.trim() || !email.trim() || !password.trim()) {
      toast.error("Barcha maydonlar to'ldirilishi shart")
      return
    }

    setLoading(true)
    try {
      const res = await authApi.login({
        restaurant_slug: restaurantSlug.trim(),
        email: email.trim(),
        password,
      })
      setTokens(res.data.access, res.data.refresh)
      const meRes = await authApi.me()
      setUser(meRes.data)
      toast.success('Xush kelibsiz')
      router.push('/dashboard')
    } catch {
      toast.error('Login yoki parol xato')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.2),_transparent_55%)] p-4 sm:p-6 lg:p-8">
      <div className="mx-auto flex min-h-screen max-w-6xl items-center justify-center">
        <div className="grid w-full overflow-hidden rounded-[32px] border border-white/40 bg-white/70 shadow-2xl shadow-sky-950/10 backdrop-blur-xl lg:grid-cols-[1.1fr_0.9fr]">
          <div className="hidden bg-slate-950 p-8 text-white lg:flex lg:flex-col lg:justify-between">
            <div>
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                <ChefHat className="h-6 w-6" />
              </div>
              <h1 className="text-3xl font-semibold">Menu</h1>
              <p className="mt-3 max-w-md text-sm text-slate-300">
                Restoran operatsiyalari, menyu, buyurtmalar va omborni bir joyda boshqaring.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 text-sm text-slate-200">
              Glassmorphism dizayn bilan tezkor va zamonaviy admin panel.
            </div>
          </div>

          <div className="p-8 sm:p-10">
            <div className="mb-8">
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-600">Tizimga kirish</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">Kabinetga kirish</h2>
              <p className="mt-2 text-sm text-slate-500">Restoran ma&apos;lumotlaringiz bilan davom eting.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <Field label="Restoran slug">
                <Input
                  value={restaurantSlug}
                  onChange={(e) => setRestaurantSlug(e.target.value)}
                  placeholder="restoran-nomi"
                  autoComplete="organization"
                />
              </Field>
              <Field label="Email">
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  autoComplete="email"
                />
              </Field>
              <Field label="Parol">
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
              </Field>
              <Button type="submit" className="w-full justify-center" disabled={loading}>
                {loading ? 'Kirish...' : 'Kirish'}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
