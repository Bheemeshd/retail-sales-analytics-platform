PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS v_sales_detail;
DROP VIEW IF EXISTS v_order_totals;
DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    signup_date TEXT NOT NULL,
    region TEXT NOT NULL CHECK (region IN ('North', 'South', 'East', 'West')),
    acquisition_channel TEXT NOT NULL,
    loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN ('None', 'Silver', 'Gold', 'Platinum'))
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    list_price REAL NOT NULL CHECK (list_price > 0),
    unit_cost REAL NOT NULL CHECK (unit_cost > 0 AND unit_cost < list_price)
);

CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    store_format TEXT NOT NULL,
    opened_date TEXT NOT NULL
);

CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    marketing_channel TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    spend REAL NOT NULL CHECK (spend > 0),
    CHECK (start_date <= end_date)
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('Store', 'Web', 'Mobile App', 'Marketplace')),
    store_id TEXT REFERENCES stores(store_id),
    campaign_id TEXT REFERENCES campaigns(campaign_id),
    status TEXT NOT NULL CHECK (status IN ('Completed', 'Returned', 'Cancelled')),
    payment_method TEXT NOT NULL,
    CHECK ((channel = 'Store' AND store_id IS NOT NULL) OR (channel <> 'Store' AND store_id IS NULL))
);

CREATE TABLE order_lines (
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    product_id TEXT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 10),
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    unit_cost REAL NOT NULL CHECK (unit_cost > 0),
    discount_pct REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 0.50),
    PRIMARY KEY (order_id, line_number)
);

CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_campaign ON orders(campaign_id);
CREATE INDEX idx_order_lines_product ON order_lines(product_id);
