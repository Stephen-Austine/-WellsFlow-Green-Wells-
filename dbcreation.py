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

# -------------------------------
# Insert default admin employee
# -------------------------------
cursor.execute("""
INSERT OR IGNORE INTO Employees (
    employee_id, first_name, last_name, phone_number, email, password,
    otp, otp_timestamp, location, role, status, last_login
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    1, "Admin", "User", 1234567890, "admin@shopfleet.com",
    hash_password("admin123"),   # real password: admin123
    "", 0, "HQ", "Admin", "Active", int(time.time())
))

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
        i, f"User{i}", f"Test{i}", 700000000 + i,
        f"user{i}@mail.com",
        hash_password("pass123"),  # real password: pass123
        "", 0, "Nairobi", "Active", int(time.time())
    ))

# -------------------------------
# Insert dummy Products
# -------------------------------
categories = {
    "Gas Cylinder": ["6kg", "12kg", "18kg", "24kg", "32kg"],
    "White Products": ["Unleaded Premium", "Low Sulphur Diesel", "Kerosine"],
    "Engine Oil": ["2kg", "1kg", "5kg", "Premium", "Fast", "Ultra"]
}

product_id = 1
for category, subs in categories.items():
    for sub in subs:
        for n in range(10):  # 10 records per subcategory
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
                random.randint(1, 5),  # user FK
                f"REG-{product_id:04d}",
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
        cargo_type, max_capacity, status, fleet_destination, last_login
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        i, f"KAA-{1000+i}", "Isuzu", f"Model-{i}", "Truck",
        int(time.time()), 1, random.randint(10000, 200000),
        100000 + i, "Fuel", random.randint(1000, 5000),
        "Active", "Nairobi", int(time.time())
    ))

# -------------------------------
# Insert dummy Orders
# -------------------------------
for i in range(1, 11):
    cursor.execute("""
    INSERT OR IGNORE INTO Orders (
        order_id, product_id, user_id, employee_id, fleet_id,
        status, product_destination, product_arrival, otp, otp_timestamp, order_timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        i, random.randint(1, product_id - 1), random.randint(1, 5),
        1, random.randint(1, 5),
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
        i, random.randint(1, product_id - 1),
        f"Review {i} for product", random.randint(1, 5),
        random.randint(1, 5), time.strftime("%Y-%m-%d %H:%M:%S"),
        "Published"
    ))

# Save and close
conn.commit()
conn.close()

print(f"Database '{db_name}' created successfully with dummy data and bcrypt-hashed passwords.")
