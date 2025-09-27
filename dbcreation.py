import sqlite3
import random
import time
import bcrypt

# Database file
db_name = "shopfleet.db"
sql_file = "shopfleet.sql"

# Connect
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Run schema
with open(sql_file, "r", encoding="utf-8") as f:
    sql_script = f.read()
cursor.executescript(sql_script)

# Utility: hash password
def hash_password(plain_text_password: str) -> str:
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ID base offsets
BASE_USER = 100_000_000
BASE_EMPLOYEE = 200_000_000
BASE_PRODUCT = 300_000_000
BASE_FLEET = 400_000_000
BASE_ORDER = 500_000_000
BASE_REVIEW = 600_000_000
BASE_CART = 700_000_000

# -------------------------------
# Insert default admin employee
# -------------------------------
cursor.execute("""
INSERT OR IGNORE INTO Employees (
    employee_id, first_name, last_name, phone_number, email, password,
    otp, otp_timestamp, location, role, status, last_login
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    BASE_EMPLOYEE + 1, "Admin", "User", 1234567890, "admin@shopfleet.com",
    hash_password("admin123"),
    "000000", int(time.time()),
    "HQ", "Admin", "Active", int(time.time())
))

# -------------------------------
# Insert extra employees
# -------------------------------
roles = {
    "Driver": 3,
    "ProductManager": 3,
    "Admin": 2,
    "Financer": 3,
    "CustomerService": 3,
    "FleetManager": 2
}

employee_id = BASE_EMPLOYEE + 2
for role, count in roles.items():
    for i in range(1, count + 1):
        cursor.execute("""
        INSERT OR IGNORE INTO Employees (
            employee_id, first_name, last_name, phone_number, email, password,
            otp, otp_timestamp, location, role, status, last_login
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            role, f"User{i}", 700000000 + employee_id % 1000,  # phone number variation
            f"{role.lower()}{i}@shopfleet.com",
            hash_password("password123"),
            "000000", int(time.time()),
            "Nairobi Depot",
            role,
            "Active",
            int(time.time())
        ))
        employee_id += 1

# -------------------------------
# Insert dummy Users
# -------------------------------
for i in range(1, 6):
    cursor.execute("""
    INSERT OR IGNORE INTO Users (
        user_id, first_name, last_name, phone_number, email, password,
        otp, otp_timestamp, location, status, last_login
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        BASE_USER + i, f"User{i}", f"Test{i}", 740000000 + i,
        f"user{i}@mail.com",
        hash_password("pass123"),
        None, None,
        "Nairobi", "Active", int(time.time())
    ))

# -------------------------------
# Insert dummy Products
# -------------------------------
categories = {
    "Gas Cylinder": ["6kg", "12kg", "18kg", "24kg", "32kg"],
    "White Products": ["Unleaded Premium", "Low Sulphur Diesel", "Kerosine"],
    "Engine Oil": ["2kg", "1kg", "5kg", "Premium", "Fast", "Ultra"]
}

product_id = BASE_PRODUCT + 1
for category, subs in categories.items():
    for sub in subs:
        for n in range(10):
            cursor.execute("""
            INSERT OR IGNORE INTO Products (
                product_id, product_name, product_category, product_description,
                product_image, product_quantity, product_cost, retail_price,
                user_id, product_registration, product_location, location_description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                f"{sub} {category}",
                category,
                f"High quality {sub} {category}",
                f"/images/{category.lower().replace(' ', '_')}_{sub.lower().replace(' ', '_')}.png",
                random.randint(10, 100),
                random.randint(500, 2000),
                random.randint(2500, 5000),
                BASE_USER + random.randint(1, 5),  # FK to Users
                f"REG-{product_id:09d}",
                "Nairobi Depot",
                f"{sub} storage section",
                "Not sold"
            ))
            product_id += 1

# -------------------------------
# Insert dummy Fleet
# -------------------------------
for i in range(1, 6):
    cursor.execute("""
    INSERT OR IGNORE INTO Fleet (
        fleet_id, registration_number, fleet_brand, fleet_model, fleet_category,
        registration_date, employee_id, fleet_mileage, chassis_number,
        cargo_type, max_capacity, status, last_login
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        BASE_FLEET + i, f"KAA-{1000+i}", "Isuzu", f"Model-{i}", "Truck",
        int(time.time()), BASE_EMPLOYEE + random.randint(2, 10),
        random.randint(10000, 200000),
        100000 + i, "Fuel", random.randint(1000, 5000),
        "Active", int(time.time())
    ))

# -------------------------------
# Insert dummy Cart items
# -------------------------------
cart_id = BASE_CART + 1
for user_id in range(1, 6):  # For each user
    user_cart_items = random.randint(1, 5)  # Each user has 1-5 cart items
    used_products = set()  # To avoid duplicate products in same cart
    
    for _ in range(user_cart_items):
        # Get a random product that hasn't been added to this user's cart yet
        product_id = BASE_PRODUCT + random.randint(1, 150)
        while product_id in used_products:
            product_id = BASE_PRODUCT + random.randint(1, 150)
        used_products.add(product_id)
        
        cursor.execute("""
        INSERT OR IGNORE INTO Cart (
            cart_id, product_id, user_id, status
        ) VALUES (?, ?, ?, ?)
        """, (
            cart_id,
            product_id,
            BASE_USER + user_id,
            random.choice(["Wishlist", "In Cart", "Saved for Later"])
        ))
        cart_id += 1

# -------------------------------
# Insert dummy Orders (now referencing cart items)
# -------------------------------
# First, get some cart items to create orders from
cursor.execute("SELECT cart_id FROM Cart LIMIT 10")
cart_items = cursor.fetchall()

for i, cart_item in enumerate(cart_items):
    cart_id = cart_item[0]
    # Get the product_id and user_id from the cart item
    cursor.execute("SELECT product_id, user_id FROM Cart WHERE cart_id = ?", (cart_id,))
    cart_data = cursor.fetchone()
    if cart_data:
        product_id, user_id = cart_data
        cursor.execute("""
        INSERT OR IGNORE INTO Orders (
            order_id, cart_id, employee_id, fleet_id,
            status, product_destination, product_arrival, otp, otp_timestamp, order_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            BASE_ORDER + i + 1,
            cart_id,
            BASE_EMPLOYEE + random.randint(2, 10),
            BASE_FLEET + random.randint(1, 5),
            random.choice(["Stage 1", "Stage 2", "Completed"]),
            "Customer Location", random.choice([0, 1]),
            str(random.randint(100000, 999999)), int(time.time()), int(time.time())
        ))

# -------------------------------
# Insert dummy Reviews
# -------------------------------
for i in range(1, 11):
    cursor.execute("""
    INSERT OR IGNORE INTO Reviews (
        review_id, product_id, text_review, ratings, user_id,
        review_timestamp, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        BASE_REVIEW + i,
        BASE_PRODUCT + random.randint(1, 150),
        f"Review {i} for product", random.randint(1, 5),
        BASE_USER + random.randint(1, 5),
        time.strftime("%Y-%m-%d %H:%M:%S"),
        "Not sold"
    ))

# Save and close
conn.commit()
conn.close()

print(f"Database '{db_name}' created successfully with namespaced IDs for employees, users, products, fleet, orders, reviews, and cart.")
print(f"Created {len(cart_items)} cart items and orders")