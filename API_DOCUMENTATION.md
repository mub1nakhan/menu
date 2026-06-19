# Restaurant OS - Complete API Documentation

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.restaurantos.com/api/v1`

## Authentication
All endpoints (except login/register) require JWT Bearer token:
```
Authorization: Bearer {access_token}
```

---

## 1. AUTHENTICATION ENDPOINTS

### Login
**POST** `/auth/login`

Request:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiI...",
  "refresh_token": "eyJhbGciOiJIUzI1NiI...",
  "token_type": "bearer"
}
```

---

### Register
**POST** `/auth/register`

Request:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "role_id": "550e8400-e29b-41d4-a716-446655440001",
  "branch_id": "550e8400-e29b-41d4-a716-446655440002",
  "phone": "+998901234567"
}
```

---

### Refresh Token
**POST** `/auth/refresh`

Request:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiI..."
}
```

---

### Get Current User
**GET** `/auth/me`

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
  "branch_id": "550e8400-e29b-41d4-a716-446655440002",
  "role_id": "550e8400-e29b-41d4-a716-446655440003",
  "is_active": true,
  "last_login_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. RESTAURANT MANAGEMENT ENDPOINTS

### List Restaurants (Admin Only)
**GET** `/restaurants`

Query Parameters:
- `skip`: 0 (pagination offset)
- `limit`: 20 (items per page)
- `is_active`: true

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Tashkent Kitchen",
    "slug": "tashkent-kitchen",
    "subscription_plan": "pro",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### Get Restaurant Details
**GET** `/restaurants/{restaurant_id}`

---

### Create Restaurant (Admin Only)
**POST** `/restaurants`

Request:
```json
{
  "name": "New Restaurant",
  "slug": "new-restaurant",
  "legal_name": "New Restaurant LLC",
  "tax_id": "123456789",
  "subscription_plan": "basic"
}
```

---

### Update Restaurant
**PUT** `/restaurants/{restaurant_id}`

Request:
```json
{
  "name": "Updated Name",
  "subscription_plan": "pro"
}
```

---

## 3. MENU MANAGEMENT ENDPOINTS

### List Menu Categories
**GET** `/restaurants/{restaurant_id}/menu/categories`

Query Parameters:
- `branch_id`: Optional branch filter
- `is_active`: true

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name_i18n": {
      "uz": "Birinchi taomlar",
      "ru": "Первые блюда",
      "en": "Appetizers"
    },
    "sort_order": 1,
    "is_active": true
  }
]
```

---

### Create Menu Category
**POST** `/restaurants/{restaurant_id}/menu/categories`

Request:
```json
{
  "name_i18n": {
    "uz": "Birinchi taomlar",
    "ru": "Первые блюда",
    "en": "Appetizers"
  },
  "sort_order": 1
}
```

---

### List Products
**GET** `/restaurants/{restaurant_id}/menu/products`

Query Parameters:
- `category_id`: Filter by category
- `branch_id`: Filter by branch
- `is_available`: true

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name_i18n": {
      "uz": "Burger",
      "en": "Burger"
    },
    "price": 25000,
    "cost": 10000,
    "prep_time_minutes": 15,
    "image_url": "https://...",
    "is_available": true
  }
]
```

---

### Create Product
**POST** `/restaurants/{restaurant_id}/menu/products`

Request:
```json
{
  "category_id": "550e8400-e29b-41d4-a716-446655440000",
  "name_i18n": {
    "uz": "Burger",
    "en": "Burger"
  },
  "price": 25000,
  "cost": 10000,
  "prep_time_minutes": 15,
  "sku": "BURGER-001"
}
```

---

## 4. ORDERS ENDPOINTS

### List Orders
**GET** `/orders`

Query Parameters:
- `status`: Filter by status (pending, preparing, ready, served, cancelled)
- `skip`: Pagination offset
- `limit`: Items per page

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "table_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "preparing",
    "total_amount": 75000,
    "items_count": 3,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### Create Order
**POST** `/orders`

Request:
```json
{
  "table_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_type": "dine_in",
  "customer_name": "John Doe",
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440001",
      "quantity": 2,
      "unit_price": 25000,
      "notes": "No onions"
    }
  ]
}
```

---

### Get Order Details
**GET** `/orders/{order_id}`

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "preparing",
  "total_amount": 75000,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "product_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 2,
      "unit_price": 25000,
      "status": "preparing",
      "notes": "No onions"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Update Order Status
**PUT** `/orders/{order_id}/status`

Request:
```json
{
  "status": "ready",
  "notes": "All items ready"
}
```

---

## 5. INVENTORY ENDPOINTS

### List Ingredients
**GET** `/inventory/ingredients`

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Meat (Beef)",
    "unit": "kg",
    "cost_per_unit": 50000,
    "reorder_level": 5
  }
]
```

---

### Create Ingredient
**POST** `/inventory/ingredients`

Request:
```json
{
  "name": "Meat (Beef)",
  "unit": "kg",
  "cost_per_unit": 50000,
  "reorder_level": 5
}
```

---

### List Recipes
**GET** `/inventory/recipes`

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "product_id": "550e8400-e29b-41d4-a716-446655440001",
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440002",
    "quantity": 0.1,
    "ingredient_name": "Meat (Beef)",
    "unit": "kg"
  }
]
```

---

### Create Recipe (BOM)
**POST** `/inventory/recipes`

Request:
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440001",
  "ingredients": [
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 0.1
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440003",
      "quantity": 1
    }
  ]
}
```

---

### Get Stock Levels
**GET** `/inventory/stock`

Query Parameters:
- `branch_id`: Required

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
    "quantity": 45.5,
    "reserved": 5,
    "available": 40.5,
    "reorder_level": 10,
    "status": "ok"
  }
]
```

---

### Record Stock Movement
**POST** `/inventory/movements`

Request:
```json
{
  "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
  "movement_type": "in",
  "quantity": 10,
  "reference_type": "purchase",
  "notes": "Weekly supply delivery"
}
```

---

## 6. PAYMENTS ENDPOINTS

### List Payments
**GET** `/payments`

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "payment_method": "card",
    "amount": 75000,
    "status": "completed",
    "transaction_id": "stripe_ch_1234567890",
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

### Create Payment
**POST** `/payments`

Request:
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_method": "card",
  "amount": 75000,
  "stripe_token": "tok_visa_1234567890"
}
```

---

## 7. ANALYTICS ENDPOINTS

### Daily Sales Report
**GET** `/analytics/daily-sales`

Query Parameters:
- `branch_id`: Required
- `from_date`: YYYY-MM-DD
- `to_date`: YYYY-MM-DD

Response:
```json
{
  "total_sales": 750000,
  "total_orders": 25,
  "avg_order_value": 30000,
  "total_tax": 75000,
  "daily_breakdown": [
    {
      "date": "2024-01-15",
      "total_sales": 250000,
      "total_orders": 10,
      "avg_order_value": 25000
    }
  ]
}
```

---

### Top Products Report
**GET** `/analytics/top-products`

Query Parameters:
- `branch_id`: Required
- `limit`: 10
- `period`: day|week|month

Response:
```json
[
  {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "product_name": "Burger",
    "quantity_sold": 45,
    "revenue": 225000,
    "profit": 90000
  }
]
```

---

### Staff Performance Report
**GET** `/analytics/staff-performance`

Query Parameters:
- `from_date`: YYYY-MM-DD
- `to_date`: YYYY-MM-DD

Response:
```json
[
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "staff_name": "Ahmed",
    "total_orders": 45,
    "total_sales": 450000,
    "commission": 45000
  }
]
```

---

## 8. WEBSOCKET ENDPOINTS

### Kitchen Display System
**WS** `/ws/kitchen/{branch_id}?token={jwt_token}`

Connection:
- Join the WebSocket at `/ws/kitchen/{branch_id}` with query parameter `token`

Messages sent to client:
```json
{
  "type": "order_update",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "preparing",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "product": "Burger",
      "quantity": 2,
      "status": "pending",
      "notes": "No onions"
    }
  ],
  "timestamp": "2024-01-15T10:35:00Z"
}
```

Messages to send from client:
```json
{
  "type": "status_update",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "ready"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting
- Rate limit: 1000 requests per hour per API key
- Headers:
  - `X-RateLimit-Limit: 1000`
  - `X-RateLimit-Remaining: 999`
  - `X-RateLimit-Reset: 1234567890`

