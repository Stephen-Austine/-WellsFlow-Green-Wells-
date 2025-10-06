# dbcreation.py
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

# Run schema (if you have a separate .sql file)
# If not, we'll define tables inline below — but based on your usage, you likely don't use shopfleet.sql
# So we'll skip executing it and rely on programmatic table creation

# Utility: hash password
def hash_password(plain_text_password: str) -> str:
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ID base offsets (your existing system)
BASE_USER = 100_000_000
BASE_EMPLOYEE = 200_000_000
BASE_PRODUCT = 300_000_000
BASE_FLEET = 400_000_000
BASE_ORDER = 500_000_000
BASE_REVIEW = 600_000_000
BASE_CART = 700_000_000
BASE_GAS_REFILL = 800_000_000  # 🔥 NEW: Gas Refill Orders

# -------------------------------
# Create Tables (if not exist)
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS `Users` (
    `user_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `first_name` TEXT NOT NULL,
    `last_name` TEXT NOT NULL,
    `phone_number` INTEGER NOT NULL,
    `email` TEXT NOT NULL UNIQUE,
    `password` TEXT NOT NULL,
    `otp` TEXT,
    `otp_timestamp` REAL,
    `location` TEXT NOT NULL,
    `status` TEXT NOT NULL DEFAULT 'Inactive',
    `last_login` REAL NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Employees` (
    `employee_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `first_name` TEXT NOT NULL,
    `last_name` TEXT NOT NULL,
    `phone_number` INTEGER NOT NULL,
    `email` TEXT NOT NULL UNIQUE,
    `password` TEXT NOT NULL,
    `otp` TEXT NOT NULL,
    `otp_timestamp` REAL NOT NULL,
    `location` TEXT NOT NULL,
    `role` TEXT NOT NULL DEFAULT 'Customer',
    `status` TEXT NOT NULL DEFAULT 'Inactive',
    `last_login` REAL NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Products` (
    `product_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `product_name` TEXT NOT NULL,
    `product_category` TEXT NOT NULL,
    `product_description` TEXT NOT NULL,
    `product_image` TEXT NOT NULL,
    `product_quantity` INTEGER NOT NULL,
    `product_cost` INTEGER NOT NULL,
    `retail_price` INTEGER NOT NULL,
    `user_id` INTEGER,
    `product_registration` TEXT NOT NULL,
    `product_location` TEXT NOT NULL,
    `location_description` TEXT,
    `status` TEXT NOT NULL DEFAULT 'Not sold',
    FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Cart` (
    `cart_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `product_id` INTEGER NOT NULL,
    `user_id` INTEGER,
    `status` TEXT NOT NULL DEFAULT 'Wishlist',
    FOREIGN KEY(`product_id`) REFERENCES `Products`(`product_id`),
    FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Orders` (
    `order_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `cart_id` INTEGER NOT NULL,
    `employee_id` INTEGER NOT NULL,
    `fleet_id` INTEGER NOT NULL,
    `status` TEXT NOT NULL DEFAULT 'Stage 1',
    `product_destination` TEXT,
    `product_arrival` REAL NOT NULL DEFAULT 'False',
    `otp` TEXT NOT NULL DEFAULT 'No OTP',
    `otp_timestamp` REAL NOT NULL DEFAULT '0',
    `order_timestamp` REAL NOT NULL,
    FOREIGN KEY(`cart_id`) REFERENCES `Cart`(`cart_id`),
    FOREIGN KEY(`employee_id`) REFERENCES `Employees`(`employee_id`),
    FOREIGN KEY(`fleet_id`) REFERENCES `Fleet`(`fleet_id`)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Fleet` (
    `fleet_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `registration_number` TEXT NOT NULL UNIQUE,
    `fleet_brand` TEXT NOT NULL,
    `fleet_model` TEXT NOT NULL,
    `fleet_category` TEXT NOT NULL,
    `registration_date` REAL NOT NULL,
    `employee_id` INTEGER NOT NULL,
    `fleet_mileage` INTEGER NOT NULL,
    `chassis_number` INTEGER NOT NULL,
    `cargo_type` TEXT NOT NULL,
    `max_capacity` INTEGER NOT NULL,
    `status` TEXT NOT NULL DEFAULT 'Inactive',
    `last_login` REAL NOT NULL,
    FOREIGN KEY(`employee_id`) REFERENCES `Employees`(`employee_id`)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS `Reviews` (
    `review_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `product_id` INTEGER NOT NULL,
    `text_review` TEXT NOT NULL,
    `ratings` INTEGER NOT NULL,
    `user_id` INTEGER NOT NULL,
    `review_timestamp` TEXT NOT NULL,
    `status` TEXT NOT NULL DEFAULT 'Not sold',
    FOREIGN KEY(`product_id`) REFERENCES `Products`(`product_id`),
    FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
""")

# 🔥 NEW TABLE: GasRefillOrders
cursor.execute("""
CREATE TABLE IF NOT EXISTS `GasRefillOrders` (
    `order_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `customer_id` INTEGER NOT NULL,
    `cylinder_type` TEXT NOT NULL,
    `size_kg` TEXT NOT NULL,
    `location` TEXT NOT NULL,
    `instructions` TEXT,
    `status` TEXT DEFAULT 'Pending',
    `order_timestamp` REAL NOT NULL,
    FOREIGN KEY(`customer_id`) REFERENCES `Users`(`user_id`)
);
""")

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
            role, f"User{i}", 700000000 + employee_id % 1000,
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
                BASE_USER + random.randint(1, 5),
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
for user_id in range(1, 6):
    user_cart_items = random.randint(1, 5)
    used_products = set()
    for _ in range(user_cart_items):
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
# Insert dummy Orders
# -------------------------------
cursor.execute("SELECT cart_id FROM Cart LIMIT 10")
cart_items = cursor.fetchall()
for i, cart_item in enumerate(cart_items):
    cart_id = cart_item[0]
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
# 🔥 Insert dummy Gas Refill Orders (for testing)
# -------------------------------
gas_cylinders = [
    ("Standard", "6kg"), ("Standard", "12kg"), ("Standard", "18kg"),
    ("Premium", "6kg"), ("Premium", "12kg")
]
locations = ["Nairobi CBD", "Westlands", "Karen", "Kasarani", "Ruiru"]
for i in range(5):
    customer_id = BASE_USER + random.randint(1, 5)
    cylinder_type, size_kg = random.choice(gas_cylinders)
    location = random.choice(locations)
    instructions = f"Gate code: {random.randint(100, 999)}" if random.random() > 0.5 else ""
    cursor.execute("""
    INSERT OR IGNORE INTO GasRefillOrders (
        order_id, customer_id, cylinder_type, size_kg, location, instructions,
        status, order_timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        BASE_GAS_REFILL + i,
        customer_id,
        cylinder_type,
        size_kg,
        location,
        instructions,
        random.choice(["Pending", "Assigned", "In Transit", "Delivered"]),
        int(time.time()) - random.randint(0, 86400)  # up to 24h ago
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

print(f"Database '{db_name}' created successfully with namespaced IDs.")
print(f"✅ Gas Refill Orders table added with sample data (IDs start at {BASE_GAS_REFILL}).")