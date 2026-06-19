-- ============================================================================
-- RESTAURANT OS - COMPLETE DATABASE SCHEMA
-- PostgreSQL 14+
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- 1. TENANCY TABLES
-- ============================================================================

CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    subscription_plan VARCHAR(20) NOT NULL DEFAULT 'trial' 
        CHECK (subscription_plan IN ('trial', 'basic', 'pro', 'enterprise')),
    subscription_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_restaurants_slug ON restaurants(slug);
CREATE INDEX idx_restaurants_active ON restaurants(is_active);

CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Tashkent',
    currency VARCHAR(10) DEFAULT 'UZS',
    phone VARCHAR(30),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (restaurant_id, name)
);
CREATE INDEX idx_branches_restaurant ON branches(restaurant_id);
CREATE INDEX idx_branches_active ON branches(is_active);

CREATE TABLE tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    table_number VARCHAR(10) NOT NULL,
    seats INT DEFAULT 4,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (branch_id, table_number)
);
CREATE INDEX idx_tables_branch ON tables(branch_id);
CREATE INDEX idx_tables_restaurant ON tables(restaurant_id);

-- ============================================================================
-- 2. ROLES & PERMISSIONS
-- ============================================================================

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (restaurant_id, code),
    UNIQUE NULLS NOT DISTINCT (restaurant_id, code) WHERE restaurant_id IS NULL
);
CREATE INDEX idx_roles_restaurant ON roles(restaurant_id);

-- ============================================================================
-- 3. USERS
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE PROTECT,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    pin_code_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (restaurant_id, email)
);
CREATE INDEX idx_users_restaurant ON users(restaurant_id);
CREATE INDEX idx_users_branch ON users(branch_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================================================
-- 4. MENU SYSTEM
-- ============================================================================

CREATE TABLE menu_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    name_i18n JSONB NOT NULL,
    description_i18n JSONB,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_menu_categories_restaurant ON menu_categories(restaurant_id);
CREATE INDEX idx_menu_categories_branch ON menu_categories(branch_id);
CREATE INDEX idx_menu_categories_active ON menu_categories(is_active);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES menu_categories(id) ON DELETE PROTECT,
    name_i18n JSONB NOT NULL,
    description_i18n JSONB,
    sku VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    prep_time_minutes INT DEFAULT 15,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_products_restaurant ON products(restaurant_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_available ON products(is_available);

-- ============================================================================
-- 5. INVENTORY SYSTEM
-- ============================================================================

CREATE TABLE ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    cost_per_unit DECIMAL(10, 4),
    reorder_level DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ingredients_restaurant ON ingredients(restaurant_id);
CREATE INDEX idx_ingredients_active ON ingredients(is_active);

CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity DECIMAL(10, 2) NOT NULL,
    UNIQUE (product_id, ingredient_id)
);
CREATE INDEX idx_recipes_product ON recipes(product_id);
CREATE INDEX idx_recipes_ingredient ON recipes(ingredient_id);

CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity DECIMAL(10, 2) NOT NULL DEFAULT 0,
    reserved DECIMAL(10, 2) DEFAULT 0,
    last_counted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (branch_id, ingredient_id)
);
CREATE INDEX idx_inventory_branch ON inventory(branch_id);
CREATE INDEX idx_inventory_ingredient ON inventory(ingredient_id);

CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    movement_type VARCHAR(20) NOT NULL 
        CHECK (movement_type IN ('in', 'out', 'adjustment', 'waste', 'count')),
    quantity DECIMAL(10, 2) NOT NULL,
    reference_type VARCHAR(50),
    reference_id UUID,
    notes TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_inventory_movements_branch ON inventory_movements(branch_id);
CREATE INDEX idx_inventory_movements_ingredient ON inventory_movements(ingredient_id);
CREATE INDEX idx_inventory_movements_type ON inventory_movements(movement_type);
CREATE INDEX idx_inventory_movements_created_at ON inventory_movements(created_at);

-- ============================================================================
-- 6. ORDERS
-- ============================================================================

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
    customer_name VARCHAR(150),
    order_type VARCHAR(20) NOT NULL 
        CHECK (order_type IN ('dine_in', 'takeout', 'delivery')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled')),
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    served_at TIMESTAMP
);
CREATE INDEX idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX idx_orders_branch ON orders(branch_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_table ON orders(table_id);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'preparing', 'ready', 'served', 'cancelled')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_status ON order_items(status);

CREATE TABLE order_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    order_item_id UUID REFERENCES order_items(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_order_status_history_order ON order_status_history(order_id);
CREATE INDEX idx_order_status_history_created_at ON order_status_history(created_at);

-- ============================================================================
-- 7. PAYMENTS
-- ============================================================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    payment_method VARCHAR(20) NOT NULL 
        CHECK (payment_method IN ('card', 'cash', 'qr_code', 'mobile')),
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id VARCHAR(100),
    gateway_response JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_payments_restaurant ON payments(restaurant_id);
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- ============================================================================
-- 8. ANALYTICS & CACHE
-- ============================================================================

CREATE TABLE daily_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    sale_date DATE NOT NULL,
    total_orders INT DEFAULT 0,
    total_sales DECIMAL(12, 2) DEFAULT 0,
    total_cost DECIMAL(12, 2) DEFAULT 0,
    total_tax DECIMAL(10, 2) DEFAULT 0,
    avg_order_value DECIMAL(10, 2) DEFAULT 0,
    UNIQUE (branch_id, sale_date)
);
CREATE INDEX idx_daily_sales_branch ON daily_sales(branch_id);
CREATE INDEX idx_daily_sales_date ON daily_sales(sale_date);

CREATE TABLE product_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    quantity_sold INT DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    cost DECIMAL(10, 2) DEFAULT 0,
    UNIQUE (product_id, date)
);
CREATE INDEX idx_product_analytics_product ON product_analytics(product_id);
CREATE INDEX idx_product_analytics_date ON product_analytics(date);

CREATE TABLE staff_commission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    commission_date DATE NOT NULL,
    total_orders INT DEFAULT 0,
    base_commission DECIMAL(10, 2) DEFAULT 0,
    bonus_commission DECIMAL(10, 2) DEFAULT 0,
    UNIQUE (user_id, commission_date)
);
CREATE INDEX idx_staff_commission_user ON staff_commission(user_id);
CREATE INDEX idx_staff_commission_date ON staff_commission(commission_date);

CREATE TABLE waste_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    ingredient_id UUID REFERENCES ingredients(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    reason VARCHAR(100),
    recorded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_waste_tracking_branch ON waste_tracking(branch_id);
CREATE INDEX idx_waste_tracking_created_at ON waste_tracking(created_at);

-- ============================================================================
-- 9. AUDIT LOG
-- ============================================================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_log_restaurant ON audit_log(restaurant_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);

-- ============================================================================
-- 10. NOTIFICATIONS
-- ============================================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150),
    message TEXT,
    notification_type VARCHAR(50),
    read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- ============================================================================
-- TRIGGERS FOR audit_updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER restaurants_updated_at BEFORE UPDATE ON restaurants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER branches_updated_at BEFORE UPDATE ON branches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER order_items_updated_at BEFORE UPDATE ON order_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

CREATE VIEW v_active_orders AS
SELECT 
    o.id,
    o.restaurant_id,
    o.branch_id,
    o.table_id,
    o.status,
    COUNT(DISTINCT oi.id) as item_count,
    SUM(oi.quantity) as total_items,
    o.total_amount,
    o.created_at
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.status NOT IN ('served', 'cancelled')
GROUP BY o.id, o.restaurant_id, o.branch_id, o.table_id, o.status, o.total_amount, o.created_at;

CREATE VIEW v_inventory_alerts AS
SELECT 
    i.id as inventory_id,
    i.restaurant_id,
    i.branch_id,
    ing.name,
    i.quantity,
    ing.reorder_level,
    CASE 
        WHEN i.quantity < ing.reorder_level THEN 'reorder'
        WHEN i.quantity = 0 THEN 'out_of_stock'
        ELSE 'ok'
    END as alert_status
FROM inventory i
JOIN ingredients ing ON i.ingredient_id = ing.id
WHERE i.quantity <= ing.reorder_level;

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

INSERT INTO restaurants (name, slug, legal_name, subscription_plan) VALUES
    ('Tashkent Kitchen', 'tashkent-kitchen', 'Tashkent Kitchen LLC', 'pro'),
    ('Samarkand Flavors', 'samarkand-flavors', 'Samarkand Flavors LLC', 'basic');

INSERT INTO branches (restaurant_id, name, city, timezone, currency) VALUES
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Downtown', 'Tashkent', 'Asia/Tashkent', 'UZS'),
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Airport', 'Tashkent', 'Asia/Tashkent', 'UZS'),
    ((SELECT id FROM restaurants WHERE slug = 'samarkand-flavors'), 'Main Branch', 'Samarkand', 'Asia/Tashkent', 'UZS');

INSERT INTO tables (restaurant_id, branch_id, table_number, seats) VALUES
    ((SELECT restaurant_id FROM branches WHERE name = 'Downtown' AND restaurant_id = (SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen')), 
     (SELECT id FROM branches WHERE name = 'Downtown' AND restaurant_id = (SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen')), 
     '1', 4),
    ((SELECT restaurant_id FROM branches WHERE name = 'Downtown' AND restaurant_id = (SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen')), 
     (SELECT id FROM branches WHERE name = 'Downtown' AND restaurant_id = (SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen')), 
     '2', 6);

INSERT INTO roles (restaurant_id, name, code, permissions) VALUES
    (NULL, 'Super Admin', 'super_admin', '["*"]'),
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Owner', 'owner', '["orders:create", "orders:read", "orders:update", "menu:manage", "staff:manage"]'),
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Manager', 'manager', '["orders:read", "menu:read", "inventory:read"]'),
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Waiter', 'waiter', '["orders:create", "orders:read"]'),
    ((SELECT id FROM restaurants WHERE slug = 'tashkent-kitchen'), 'Chef', 'chef', '["orders:read", "orders:update"]);

