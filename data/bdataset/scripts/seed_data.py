import sqlite3
import pathlib
import random 
from faker import Faker 
from datetime import date, timedelta

fake = Faker("en_US")
random.seed(42)
Faker.seed(42)

BASE_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = BASE_DIR / "business.sqlite"
SCHEMA_PATH = BASE_DIR / "schema.sql"

# Dummy Data

# Functions 

def random_date(start="2000-01-01", end="2026-09-22"): 
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    delta = (e - s).days
    return str(s + timedelta(days=random.randint(0, delta)))

def initialize_db(conn): 
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()


# Reference Table 
REGIONS = [
    (1, "North", "Germany"),
    (2, "East", "Germany"),
    (3, "West", "Germany"),
    (4, "South", "Germany"),
    (5, "North", "Ireland"),
    (6, "East", "Ireland"),
    (7, "West", "Ireland"),
    (9, "South", "Ireland"),
]

SEGMENTS = [
    (1, "Retail",      "Retail customers"),
    (2, "Wholesale",   "Wholesale customers"),
    (3, "Enterprise",  "Enterprise customers"),
]

CATEGORIES = [
    (1, "Hardware",      None),
    (2, "Software",      None),
    (3, "Electronics",   None),
    (4, "Laptops",       1),      # → Hardware
    (5, "Desktops",      1),      # → Hardware
    (6, "Peripherals",   1),      # → Hardware
    (7, "OS",            2),      # → Software
    (8, "Productivity",  2),      # → Software
    (9, "Smartphones",   3),      # → Electronics
    (10, "Audio",        3),      # → Electronics
]

def seed_references(conn):
    conn.executemany(
        "INSERT INTO regions (id, name_regions, country) VALUES (?, ?, ?)",
        REGIONS
    )
    conn.executemany(
        "INSERT INTO customer_segments (id, name_customer_segments, description_customer_segments) VALUES (?, ?, ?)",
        SEGMENTS
    )
    conn.executemany(
        "INSERT INTO product_categories (id, name_product_categories, parent_category_id) VALUES (?, ?, ?)",
        CATEGORIES 
    )
    conn.commit()
    print(f"References added")


# Products
PRODUCTS = [
    ("ThinkPad X1 Carbon",      4,  1299.99, 780.00,  45),
    ("Dell XPS 15",             4,  1799.99, 1050.00, 30),
    ("MacBook Pro 14",          4,  2499.99, 1500.00, 20),
    ("HP EliteBook 840",        4,   999.99,  600.00, 60),
    ("Lenovo IdeaPad 5",        4,   649.99,  390.00, 80),
    ("Dell OptiPlex 7090",      5,   899.99,  540.00, 35),
    ("HP ProDesk 400",          5,   749.99,  450.00, 25),
    ("Logitech MX Keys",        6,   119.99,   60.00, 150),
    ("Logitech MX Master 3",    6,    99.99,   50.00, 200),
    ("Dell U2722D Monitor",     6,   549.99,  330.00, 40),
    ("Windows 11 Pro",          7,   199.99,   20.00, 999),
    ("Ubuntu Pro",              7,    49.99,    5.00, 999),
    ("Microsoft 365 Business",  8,   149.99,   30.00, 999),
    ("Adobe Creative Cloud",    8,   599.99,  120.00, 999),
    ("Samsung Galaxy S24",      9,   999.99,  600.00, 55),
    ("iPhone 15 Pro",           9,  1199.99,  720.00, 40),
    ("Sony WH-1000XM5",        10,   349.99,  175.00, 70),
    ("Apple AirPods Pro",      10,   279.99,  140.00, 90),
    ("Jabra Evolve2 75",       10,   449.99,  225.00, 30),
    ("Razer BlackWidow V4",     6,   149.99,   75.00, 60),
]

def seed_products(conn): 
    rows_products = [
        (i + 1, name, cat, price, cost, stock) for i, (name, cat, price, cost, stock) in enumerate(PRODUCTS)
    ]
    conn.executemany(
        "INSERT INTO products (id, name_products, product_category_id, unit_price, unit_cost, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)", 
        rows_products
    )
    conn.commit()
    print(f"Products ({len(rows_products)}) added")
    return len(rows_products)

# Employees 
ROLES = ["sales", "sales", "sales", "support", "management"]

def seed_employees(conn, n= 30): 
    region_ids = [r[0] for r in REGIONS]
    rows_employees = []
    for i in range(1, n+1): 
        rows_employees.append((
            i, 
            fake.name(), 
            fake.unique.email(), 
            random.choice(ROLES), 
            random_date("2000-01-01", "2026-09-22"), 
            random.choice(region_ids)
        ))
    conn.executemany(
        "INSERT INTO employees (id, name_employees, email, role_employees, hire_date, region_id) VALUES (?, ?, ?, ?, ?, ?)",
        rows_employees
    )
    conn.commit()
    print(f"Employees ({len(rows_employees)}) added")
    return len(rows_employees)


# Customer 
def seed_customer(conn, n=200):
    region_ids = [r[0] for r in REGIONS]
    segment_ids = [s[0] for s in SEGMENTS]
    rows_customer = []
    for i in range(1, n+1):
        rows_customer.append((
            i, 
            fake.name(),
            fake.unique.email(), 
            random.choice(region_ids), 
            random.choice(segment_ids), 
            random_date("2000-01-01", "2026-09-22"), 
            random.choices([1, 0], weights=[85, 15])[0], # choice between active (1) and inactive (0) 85 to 15 %
        )) 
    conn.executemany(
        "INSERT INTO customers (id, name_customers, email, region_id, customer_segment_id, sign_up_date, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)", 
        rows_customer
    )
    conn.commit()
    print(f"Customers ({len(rows_customer)}) added")
    return len(rows_customer)

# Orders, Items, Payments
STATUSES  = ["pending", "shipped", "delivered", "delivered", "delivered", "cancelled"]
CHANNELS  = ["web", "web", "phone", "partner"]
METHODS   = ["credit_card", "credit_card", "paypal", "bank_transfer"]
N_PRODUCTS = len(PRODUCTS)

def seed_orders(conn, n_customers, n_employees, n_orders=800):
    orders = []
    order_items = []
    payments = []

    order_id = 1
    item_id = 1
    payment_id = 1

    for _ in range(n_orders):
        customer_id = random.randint(1, n_customers)
        employee_id = random.randint(1, n_employees) if random.random() > 0.1 else None
        order_date = random_date("2000-01-01", "2026-09-22")
        status = random.choice(STATUSES)
        ship_date = None
        if status in ("shipped", "delivered"):
            od = date.fromisoformat(order_date)
            ship_date = str(od + timedelta(days=random.randint(1, 7)))

        orders.append((
            order_id, customer_id, employee_id,
            order_date, ship_date, status,
            random.choice(CHANNELS),
        ))

        n_items = random.randint(1, 4)
        product_ids = random.sample(range(1, N_PRODUCTS + 1), min(n_items, N_PRODUCTS))
        order_total = 0.0

        for pid in product_ids:
            product_name, cat, unit_price, cost, stock = PRODUCTS[pid - 1]
            qty = random.randint(1, 5)
            discount = random.choices([0.0, 0.05, 0.10, 0.15], weights=[60, 20, 15, 5])[0]
            order_items.append((item_id, order_id, pid, qty, unit_price, discount))
            order_total += qty * unit_price * (1 - discount)
            item_id += 1
        if status not in ("pending", "cancelled"):
            od = date.fromisoformat(order_date)
            pay_date = str(od + timedelta(days=random.randint(0, 3)))
            payments.append((
                payment_id, order_id, pay_date,
                round(order_total, 2),
                random.choice(METHODS),
            ))
            payment_id += 1

        order_id += 1

    conn.executemany(
        "INSERT INTO orders (id, customer_id, employee_id, order_date, ship_date, status, channel) VALUES (?, ?, ?, ?, ?, ?, ?)",
        orders
    )
    conn.executemany(
        "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, discount) VALUES (?, ?, ?, ?, ?, ?)",
        order_items
    )
    conn.executemany(
        "INSERT INTO payments (id, order_id, payment_date, amount, payment_method) VALUES (?, ?, ?, ?, ?)",
        payments
    )
    conn.commit()
    print(f"  orders ({len(orders)}), order_items ({len(order_items)}), payments ({len(payments)})")

def main(): 
    if DB_PATH.exists(): 
        DB_PATH.unlink()
        print("Deleting old database")
    conn = sqlite3.connect(DB_PATH)

    print("Read the Schema: ")
    initialize_db(conn)

    print("Add Data: ")
    seed_references(conn)
    n_products  = seed_products(conn)
    n_employees = seed_employees(conn, n=30)
    n_customers = seed_customer(conn, n=200)
    seed_orders(conn, n_customers, n_employees, n_orders=800)

    print("Summary: ")
    tables = ["regions", "customer_segments", "product_categories",
              "customers", "products", "employees",
              "orders", "order_items", "payments"]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<25} {count:>5} rows")
 
    conn.close()
    print(f"\n Done! Database: {DB_PATH}")

if __name__ == "__main__": 
    main()