# Restaurant OS - Complete Frontend Implementation Guide

## Overview
Four separate Next.js applications:
1. **Customer App** - QR-based ordering (mobile-first)
2. **Waiter App** - Order management and table selection
3. **Chef App** - Kitchen Display System (KDS)
4. **Admin App** - Dashboard, analytics, and management

---

## Shared Frontend Setup

### Requirements
```json
{
  "node": ">=18.0.0",
  "npm": ">=9.0.0"
}
```

### Shared Dependencies (package.json)
```json
{
  "dependencies": {
    "next": "14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "react-query": "^3.39.0",
    "@tanstack/react-query": "^5.0.0",
    "socket.io-client": "^4.7.0",
    "framer-motion": "^10.16.0",
    "tailwindcss": "^3.3.0",
    "shadcn-ui": "^0.8.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "lucide-react": "^0.263.0",
    "date-fns": "^2.30.0",
    "zustand-persist": "^1.0.0",
    "i18next": "^23.5.0",
    "react-i18next": "^13.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.0.0"
  }
}
```

---

## 1. CUSTOMER APP (QR-Based Ordering)

### Directory Structure
```
frontend/customer-app/
├── public/
│   ├── images/
│   └── icons/
├── src/
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── _document.tsx
│   │   ├── index.tsx              # Landing/QR scan
│   │   ├── [table_id]/
│   │   │   ├── menu.tsx           # Menu display
│   │   │   ├── cart.tsx           # Shopping cart
│   │   │   ├── checkout.tsx       # Checkout
│   │   │   └── order-status.tsx   # Order tracking
│   │   └── api/
│   │       └── [...].ts           # API routes
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── menu/
│   │   │   ├── MenuCategory.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductDetails.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── cart/
│   │   │   ├── CartSummary.tsx
│   │   │   ├── CartItem.tsx
│   │   │   └── CheckoutForm.tsx
│   │   └── order/
│   │       ├── OrderStatus.tsx
│   │       ├── OrderTimeline.tsx
│   │       └── NotificationBell.tsx
│   ├── hooks/
│   │   ├── useCart.ts
│   │   ├── useMenu.ts
│   │   ├── useOrder.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── cartStore.ts
│   │   ├── sessionStore.ts
│   │   └── authStore.ts
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts
│   │   └── models.ts
│   ├── utils/
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── helpers.ts
│   ├── i18n/
│   │   ├── en.json
│   │   ├── uz.json
│   │   └── ru.json
│   └── styles/
│       ├── globals.css
│       ├── tailwind.css
│       └── theme.css
├── .env.local
├── .env.local.example
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

### Key Features
- QR code scanning with `jsqr`
- Real-time menu with multi-language support
- Live order tracking with WebSocket
- Cart management with localStorage
- Payment integration (Stripe)
- Mobile-first responsive design
- Offline support with Service Workers

### Page Structure

**QR Scan (index.tsx)**
- QR code reader component
- Auto-redirect to table after scan
- Error handling and retry

**Menu (menu.tsx)**
- Category tabs
- Product listing with images
- Add to cart with customization
- Search and filter
- i18n support

**Cart (cart.tsx)**
- Item list with remove option
- Quantity adjustment
- Promo code input
- Total calculation with tax

**Checkout (checkout.tsx)**
- Stripe payment form
- Order review
- Confirm order

---

## 2. WAITER APP (Order Management)

### Directory Structure
```
frontend/waiter-app/
├── src/
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── login.tsx              # PIN/email login
│   │   ├── dashboard.tsx          # Main screen
│   │   ├── tables/
│   │   │   ├── [table_id].tsx     # Table orders
│   │   │   └── create-order.tsx   # New order
│   │   ├── active-orders.tsx      # All orders
│   │   └── settings.tsx           # Waiter settings
│   ├── components/
│   │   ├── layout/
│   │   │   ├── WaiterLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── NavBar.tsx
│   │   ├── tables/
│   │   │   ├── TableGrid.tsx
│   │   │   ├── TableCard.tsx
│   │   │   └── TableStatus.tsx
│   │   ├── orders/
│   │   │   ├── OrderForm.tsx
│   │   │   ├── OrderList.tsx
│   │   │   ├── OrderItem.tsx
│   │   │   ├── OrderEditing.tsx
│   │   │   └── PrintBill.tsx
│   │   └── modals/
│   │       ├── NewOrderModal.tsx
│   │       ├── ModifyOrderModal.tsx
│   │       └── PaymentModal.tsx
│   ├── hooks/
│   │   ├── useWaiter.ts
│   │   ├── useOrders.ts
│   │   └── useTables.ts
│   ├── store/
│   │   ├── waiterStore.ts
│   │   └── orderStore.ts
│   └── ...
├── Dockerfile
├── next.config.js
├── tsconfig.json
└── package.json
```

### Key Features
- PIN-based quick login
- Table grid visualization with status
- Drag-and-drop order management
- Quick order creation
- Order modification
- Bill printing
- Real-time order updates via WebSocket
- Offline order queuing

### Page Structure

**Login (login.tsx)**
- PIN code input (4-6 digits)
- Email/password fallback
- Restaurant selection

**Dashboard (dashboard.tsx)**
- Table grid with status colors
- Quick stats (active orders, total sales)
- Recently served tables

**Table Orders ([table_id].tsx)**
- Orders for specific table
- Add items to existing order
- Modify quantities
- View order timeline

---

## 3. CHEF APP (Kitchen Display System)

### Directory Structure
```
frontend/chef-app/
├── src/
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── login.tsx              # Chef login
│   │   ├── kds.tsx                # Kitchen Display
│   │   ├── summary.tsx            # Daily summary
│   │   └── settings.tsx           # Chef settings
│   ├── components/
│   │   ├── layout/
│   │   │   ├── ChefLayout.tsx
│   │   │   └── Header.tsx
│   │   ├── kds/
│   │   │   ├── OrderBoard.tsx     # Main KDS view
│   │   │   ├── OrderCard.tsx      # Individual order
│   │   │   ├── OrderItem.tsx      # Food item card
│   │   │   ├── StatusButton.tsx   # Status update button
│   │   │   ├── Timer.tsx          # Prep time timer
│   │   │   └── Filter.tsx         # Filter/category
│   │   ├── alerts/
│   │   │   ├── OrderAlert.tsx     # New order sound/visual
│   │   │   └── StockAlert.tsx     # Low stock alert
│   │   └── modals/
│   │       └── OrderDetailsModal.tsx
│   ├── hooks/
│   │   ├── useKitchen.ts
│   │   ├── useOrders.ts
│   │   └── useSound.ts
│   ├── services/
│   │   └── websocket.ts           # Kitchen WebSocket
│   ├── store/
│   │   ├── kitchenStore.ts
│   │   └── orderStore.ts
│   ├── utils/
│   │   ├── printer.ts             # Kitchen printer
│   │   └── audio.ts               # Alert sounds
│   └── ...
├── public/
│   └── sounds/
│       ├── order-alert.mp3
│       └── ready-alert.mp3
├── Dockerfile
└── package.json
```

### Key Features
- Live order board with WebSocket
- Color-coded status (pending, preparing, ready)
- Sound alerts for new orders
- Order timer showing prep time
- Filter by category/station
- Drag-and-drop reordering
- Kitchen printer integration
- Offline support
- Full-screen mode
- Responsive for small displays

### Order Display
- **Pending** (Red): New orders
- **Preparing** (Yellow): Being cooked
- **Ready** (Green): Ready for service
- **Served**: Complete

---

## 4. ADMIN APP (Dashboard & Analytics)

### Directory Structure
```
frontend/admin-app/
├── src/
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── login.tsx
│   │   ├── dashboard.tsx          # Main dashboard
│   │   ├── restaurants/
│   │   │   ├── index.tsx          # List restaurants
│   │   │   ├── [id]/
│   │   │   │   ├── settings.tsx   # Settings
│   │   │   │   └── staff.tsx      # Staff management
│   │   │   └── create.tsx         # Create new
│   │   ├── branches/
│   │   │   ├── index.tsx
│   │   │   ├── [id].tsx
│   │   │   └── create.tsx
│   │   ├── menu/
│   │   │   ├── categories.tsx
│   │   │   ├── products.tsx       # Product management
│   │   │   └── recipes.tsx        # Recipe (BOM)
│   │   ├── inventory/
│   │   │   ├── stock.tsx          # Stock levels
│   │   │   ├── movements.tsx      # History
│   │   │   ├── ingredients.tsx    # Ingredients
│   │   │   └── adjustments.tsx    # Manual adjustments
│   │   ├── analytics/
│   │   │   ├── sales.tsx          # Sales dashboard
│   │   │   ├── products.tsx       # Product analytics
│   │   │   ├── staff.tsx          # Staff performance
│   │   │   └── waste.tsx          # Waste tracking
│   │   ├── staff/
│   │   │   ├── index.tsx          # Staff list
│   │   │   ├── [id].tsx           # Staff details
│   │   │   └── create.tsx         # Add staff
│   │   ├── payments/
│   │   │   ├── transactions.tsx
│   │   │   └── reports.tsx
│   │   ├── settings.tsx           # System settings
│   │   └── profile.tsx            # Owner profile
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AdminLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── Footer.tsx
│   │   ├── dashboard/
│   │   │   ├── StatCard.tsx
│   │   │   ├── Chart.tsx
│   │   │   ├── RecentOrders.tsx
│   │   │   └── QuickStats.tsx
│   │   ├── menu/
│   │   │   ├── CategoryForm.tsx
│   │   │   ├── ProductForm.tsx
│   │   │   ├── ProductList.tsx
│   │   │   ├── RecipeForm.tsx
│   │   │   └── ImageUpload.tsx
│   │   ├── inventory/
│   │   │   ├── StockTable.tsx
│   │   │   ├── MovementHistory.tsx
│   │   │   ├── AdjustmentForm.tsx
│   │   │   └── AlertsList.tsx
│   │   ├── analytics/
│   │   │   ├── SalesChart.tsx
│   │   │   ├── ProductChart.tsx
│   │   │   ├── HourlyChart.tsx
│   │   │   └── WasteChart.tsx
│   │   ├── tables/
│   │   │   ├── DataTable.tsx
│   │   │   ├── Pagination.tsx
│   │   │   └── Filters.tsx
│   │   ├── forms/
│   │   │   ├── RestaurantForm.tsx
│   │   │   ├── BranchForm.tsx
│   │   │   └── StaffForm.tsx
│   │   └── modals/
│   │       ├── ConfirmDialog.tsx
│   │       └── FormModal.tsx
│   ├── hooks/
│   │   ├── useAdmin.ts
│   │   ├── useAnalytics.ts
│   │   ├── useInventory.ts
│   │   ├── useMenu.ts
│   │   ├── useRestaurant.ts
│   │   └── useDataTable.ts
│   ├── services/
│   │   ├── analytics.ts
│   │   ├── inventory.ts
│   │   ├── menu.ts
│   │   ├── restaurant.ts
│   │   └── export.ts             # Excel/PDF export
│   ├── store/
│   │   ├── adminStore.ts
│   │   ├── analyticsStore.ts
│   │   └── filters.ts
│   ├── charts/
│   │   └── config.ts             # Chart.js config
│   └── ...
├── Dockerfile
└── package.json
```

### Key Features
- **Dashboard**: Real-time KPIs
- **Menu Management**: Full CRUD for categories/products
- **Inventory**: Stock tracking, movements, alerts
- **Analytics**: Sales, products, waste, staff performance
- **Staff Management**: Roles, permissions, commissions
- **Reports**: Generate/export to Excel/PDF
- **Settings**: Restaurant configuration
- **Multi-branch support**

### Dashboards

**Sales Dashboard**
- Daily/weekly/monthly sales
- Revenue vs target
- Order count
- Average bill
- Peak hours

**Inventory Dashboard**
- Low stock alerts
- Stock movements
- Waste tracking
- Ingredient costs

**Product Analytics**
- Top 10 products
- Slow products
- Profit margins
- Popular combinations

---

## Deployment Structure

### Docker Setup per App
Each app has its own `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json .
RUN npm ci
COPY . .

ENV NEXT_PUBLIC_API_URL=http://backend:8000
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables
Each app has `.env.local.example`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_STRIPE_KEY=pk_test_...
NEXT_PUBLIC_LANGUAGE=en
```

---

## State Management (Zustand)

### Cart Store (Customer App)
```typescript
interface CartStore {
  items: CartItem[]
  addItem: (item: CartItem) => void
  removeItem: (id: string) => void
  updateQuantity: (id: string, qty: number) => void
  clear: () => void
  total: () => number
}
```

### Order Store (All Apps)
```typescript
interface OrderStore {
  orders: Order[]
  activeOrder: Order | null
  setOrders: (orders: Order[]) => void
  updateOrder: (id: string, data: Partial<Order>) => void
  removeOrder: (id: string) => void
}
```

---

## Real-Time Updates (WebSocket)

All apps subscribe to order updates:
```typescript
const socket = io(WS_URL, {
  query: { token: authToken }
});

socket.on('order_update', (data) => {
  store.updateOrder(data.order_id, data);
});
```

---

## Testing Strategy

```bash
# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

