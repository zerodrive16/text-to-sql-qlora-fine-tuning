-- References --
CREATE TABLE regions (
    id              INTEGER PRIMARY KEY,
    name_regions    TEXT NOT NULL, -- north, east, south, west
    country         TEXT NOT NULL  -- country
);
 
CREATE TABLE customer_segments (
    id                              INTEGER PRIMARY KEY,
    name_customer_segments          TEXT NOT NULL, -- retail, wholesale, enterprise
    description_customer_segments   TEXT
);
 
CREATE TABLE product_categories (
    id                      INTEGER PRIMARY KEY,
    name_product_categories TEXT NOT NULL, -- Hardware, Software, Electronics
    parent_category_id      INTEGER REFERENCES product_categories(id)
);
 
 
-- Business tables --
 
CREATE TABLE customers (
    id                  INTEGER PRIMARY KEY,
    name_customers      TEXT NOT NULL,
    email               TEXT UNIQUE,
    region_id           INTEGER REFERENCES regions(id),
    customer_segment_id INTEGER REFERENCES customer_segments(id),
    sign_up_date        TEXT NOT NULL, -- yyyy-mm-dd
    is_active           INTEGER NOT NULL DEFAULT 1 -- 1 = active, 0 = inactive
);
 
CREATE TABLE products (
    id                  INTEGER PRIMARY KEY,
    name_products       TEXT NOT NULL,
    product_category_id INTEGER REFERENCES product_categories(id),
    unit_price          REAL NOT NULL,
    stock_quantity      INTEGER NOT NULL DEFAULT 0
);
 
CREATE TABLE employees (
    id              INTEGER PRIMARY KEY,
    name_employees  TEXT NOT NULL,
    email           TEXT UNIQUE,
    role_employees  TEXT NOT NULL, -- sales, support, management
    hire_date       TEXT NOT NULL, -- yyyy-mm-dd
    region_id       INTEGER REFERENCES regions(id)
);
 
 
-- Transactional tables --
 
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    employee_id INTEGER REFERENCES employees(id),
    order_date  TEXT NOT NULL, -- yyyy-mm-dd
    ship_date   TEXT           -- yyyy-mm-dd
);
 
CREATE TABLE order_items (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount   REAL NOT NULL DEFAULT 0.00 -- percentage discount applied to the item
);
 
CREATE TABLE payments (
    id             INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL REFERENCES orders(id),
    payment_date   TEXT NOT NULL,    -- yyyy-mm-dd
    amount         REAL NOT NULL,
    payment_method TEXT NOT NULL     -- credit card, paypal, bank transfer
);