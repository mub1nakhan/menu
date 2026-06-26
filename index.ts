// ── Auth ──────────────────────────────────────────────────────────────────────
export interface LoginPayload {
  restaurant_slug: string
  email: string
  password: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface CurrentUser {
  id: string
  email: string
  full_name: string
  restaurant_id: string
  restaurant_name: string
  branch_id: string | null
  role_code: 'super_admin' | 'owner' | 'branch_manager' | 'waiter' | 'chef' | 'cashier'
}

// ── Restaurant / Branch ───────────────────────────────────────────────────────
export interface Branch {
  id: string
  name: string
  address: string | null
  city: string | null
  timezone: string
  currency: string
  phone: string | null
  latitude: string | null
  longitude: string | null
  is_active: boolean
  created_at: string
}

// ── Menu ──────────────────────────────────────────────────────────────────────
export interface I18nField {
  uz?: string
  ru?: string
  en?: string
}

export interface MenuCategory {
  id: string
  branch: string | null
  name_i18n: I18nField
  sort_order: number
  is_active: boolean
  created_at: string
}

export interface Product {
  id: string
  branch: string | null
  category: string
  name_i18n: I18nField
  description_i18n: I18nField
  image_url: string | null
  price: string
  cost_price: string | null
  is_available: boolean
  prep_time_minutes: number | null
  sort_order: number
  margin: number | null
  created_at: string
}

// ── Orders ────────────────────────────────────────────────────────────────────
export type OrderStatus =
  | 'pending' | 'confirmed' | 'preparing'
  | 'ready' | 'served' | 'completed' | 'cancelled'

export type OrderSource = 'qr_customer' | 'waiter' | 'pos'

export interface Table {
  id: string
  branch: string
  label: string
  capacity: number
  qr_code_token: string
  status: 'free' | 'occupied' | 'reserved' | 'cleaning'
}

export interface OrderItem {
  id: string
  product: string
  product_name?: string
  quantity: number
  unit_price: string
  line_total: string
  status: string
  special_instructions: string | null
}

export interface Order {
  id: string
  order_number: string
  branch: string
  table: string | null
  source: OrderSource
  status: OrderStatus
  subtotal: string
  discount_amount: string
  tax_amount: string
  total_amount: string
  notes: string | null
  items: OrderItem[]
  created_at: string
}

// ── Inventory ─────────────────────────────────────────────────────────────────
export interface Ingredient {
  id: string
  name: string
  unit: string
  unit_cost: string
  low_stock_threshold: string
}

export interface InventoryItem {
  id: string
  ingredient: string
  ingredient_name?: string
  quantity_on_hand: string
  updated_at: string
}

// ── Payments ──────────────────────────────────────────────────────────────────
export interface Payment {
  id: string
  order: string
  method: 'cash' | 'card' | 'online' | 'wallet'
  status: 'pending' | 'authorized' | 'paid' | 'failed' | 'refunded' | 'partially_refunded'
  amount: string
  currency: string
  paid_at: string | null
  created_at: string
}

// ── Pagination ────────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ── Dashboard stats ───────────────────────────────────────────────────────────
export interface DashboardStats {
  today_revenue: number
  today_orders: number
  active_orders: number
  low_stock_count: number
}