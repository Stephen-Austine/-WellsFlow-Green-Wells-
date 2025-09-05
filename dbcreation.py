import sqlite3

# Name of your output database file
db_name = "shopfleet.db"

# Name of your exported SQL file
sql_file = "shopfleet.sql"

# Connect (this creates the .db file)
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Read and execute the SQL commands
with open(sql_file, "r", encoding="utf-8") as f:
    sql_script = f.read()

cursor.executescript(sql_script)

# Insert default admin user into Employees table
cursor.execute("""
INSERT OR IGNORE INTO Employees (
    employee_id, first_name, last_name, phone_number, email, password,
    otp, otp_timestamp, location, role, status, last_login
) VALUES (
    1, 'Admin', 'User', 1234567890, 'admin@shopfleet.com', 'admin123',
    '', 0, 'HQ', 'Admin', 'Active', strftime('%s','now')
);
""")

# Save and close
conn.commit()
conn.close()

print(f"Database '{db_name}' created successfully from '{sql_file}' with default admin user.")
