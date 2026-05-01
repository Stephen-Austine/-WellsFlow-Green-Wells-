# WellsFlow — GreenWells Business Management System

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Flask-Login](https://img.shields.io/badge/Flask--Login-Auth-4B8BBE?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

WellsFlow is a full-stack business management web application built for company dealing in petroleum products, lubricants, and fleet logistics. The system unifies customer-facing e-commerce, internal fleet management, gas refill ordering, employee administration, and financial reporting into one platform.

---

## Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [User Roles & Access Control](#-user-roles--access-control)
- [Application Modules](#-application-modules)
- [Getting Started](#-getting-started)
- [Configuration](#️-configuration)
- [Authentication Flow](#-authentication-flow)
- [Known Issues & Limitations](#-known-issues--limitations)

---

## Features

- **E-Commerce Shop** — Product browsing, cart management, checkout, and order tracking
- **Fleet Management** — Vehicle registration, assignment, fleet order management, and driver dashboards
- **Gas Refill Ordering** — Customer-facing cylinder refill requests with admin approval workflow
- **Bulk Orders** — Wholesale/bulk product ordering with a dedicated management interface
- **Employee Management** — Add, edit, filter, and manage employees by role and status
- **Production Management** — Manage product listings, stock, pricing, and images
- **Finance Dashboard** — Financial overview accessible to the Financer role
- **Reports** — Business reporting for management
- **OTP Authentication** — Two-factor login via email OTP with 90-second expiry
- **Role-Based Access Control** — Granular route protection per employee role
- **Customer Order Tracking** — Real-time order status pages for shop and gas refill orders

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, Flask 2.x |
| **Database** | SQLite (via `sqlite3`) |
| **ORM / Models** | Flask-SQLAlchemy (models), raw `sqlite3` (routes) |
| **Authentication** | Flask-Login, bcrypt password hashing, email OTP |
| **Forms** | Flask-WTF, WTForms |
| **Templating** | Jinja2 (HTML templates) |
| **Styling** | Custom CSS (`static/css/styles.css`) |
| **Email** | SMTP via Gmail (smtplib) |
| **Session Management** | Flask server-side sessions (cart state) |

---

## Project Structure

```
greenwells_wellsflow/
│
├── app.py                        # Main Flask app, routes, role_required decorator
├── config.py                     # App configuration
├── extensions.py                 # Flask extensions init (SQLAlchemy)
├── models.py                     # SQLAlchemy models (User, Product, Order, Fleet, FleetOrder)
├── forms.py                      # WTForms: SignupForm, LoginForm
├── forms_fleet.py                # WTForms: Fleet-related forms
├── decorators.py                 # Custom decorators (admin_required)
├── user_object.py                # UserObject class for Flask-Login integration
├── utils.py                      # Shared utilities
├── patch_db.py                   # DB migration / patching script
├── testping.py                   # Connectivity / ping test utility
│
├── routes/
│   ├── __init__.py               # Auto-registers all blueprints
│   ├── auth.py                   # Authentication: login, signup, OTP, logout
│   ├── fleet.py                  # Fleet ordering (customer requests + admin view)
│   ├── gasrefill.py              # Gas refill orders (customer + admin dashboard)
│   ├── shop.py                   # E-commerce: shop, cart, checkout, orders
│   └── employees.py              # Employee management (Admin only)
│
├── templates/
│   ├── base.html                 # Main landing page layout
│   ├── base2.html                # Alternate base layout
│   ├── auth/                     # login, signup, otp_verify, forgot_password
│   ├── shop/                     # shop_home, cart, checkout, order_tracking, bulk
│   ├── fleet/                    # customer_request, orders_list, admin views
│   │   ├── adminside_fleet/      # dashboard, vehicles, employees, finances, reports
│   │   └── fleet_extend/         # orders, production, vehicles, customers, employees
│   └── gasrefill/                # customer_request, order_tracking, admin_dashboard
│
├── static/
│   ├── css/styles.css
│   ├── img/                      # Hero images (fleet.jpg, shop.jpg, bulk.jpg)
│   └── uploads/                  # Product images
│
├── instance/
│   └── shopfleet.db              # SQLite database (gitignore in production)
│
├── dbcreation.py                 # DB initialization and seed data script
├── shopfleetorg.sql              # Raw SQL schema definition
└── sql.py                        # Additional SQL utilities
```

---

## Database Schema

The app uses a single SQLite database (`shopfleet.db`) with the following core tables:

| Table | Description |
|---|---|
| `Users` | Customer accounts — name, email, phone, password hash, OTP, location, status |
| `Employees` | Staff accounts — name, email, role, OTP, status |
| `Products` | Product catalog — name, category, description, image, quantity, cost, retail price, status |
| `Fleet` | Vehicle registry — reg number, brand, model, category, mileage, cargo type, capacity, status |
| `Orders` | Customer shop orders — cart_id, employee_id, fleet_id, status, delivery OTP |
| `Cart` | Shopping cart items — user_id, product_id, quantity |
| `FleetOrders` | Fleet hire requests — user_id, cargo type, destination, duration, status, timestamps |
| `FleetOrderAssignments` | Links fleet orders to specific vehicles |
| `GasRefillOrders` | Gas cylinder refill requests — user_id, cylinder type, size, location, status |
| `BulkOrders` | Wholesale purchase orders |

**ID Range Offsets (prevents table collision):**

```
Users:                  100,000,000+
Employees:              200,000,000+
Products:               300,000,000+
Fleet:                  400,000,000+
Orders:                 500,000,000+
GasRefillOrders:        800,000,000+
FleetOrders:            900,000,000+
FleetOrderAssignments: 1,000,000,000+
BulkOrders:            1,100,000,000+
```

---

## User Roles & Access Control

Routes are protected with a custom `role_required` decorator defined in `app.py`.

| Role | Access |
|---|---|
| `customer` | Shop, cart, checkout, fleet requests, gas refill, order tracking |
| `Driver` | Dashboard, assigned vehicle and fleet order views |
| `FleetManager` | Dashboard, all vehicle and fleet order management |
| `Productmanager` | Production management (add/edit/manage products) |
| `Customerservice` | Customer management, order management, gas refill admin |
| `Financer` | Finance dashboard, gas refill admin |
| `Admin` | Full access to all routes including employee management |

Usage example:

```python
@app.route("/dashboard")
@role_required(['Driver', 'Admin', 'FleetManager'])
def dashboard():
    ...
```

Unauthorized users are redirected to their role's default page rather than a generic error, preventing redirect loops.

---

## Application Modules

### Authentication (`routes/auth.py`)

| Route | Method | Description |
|---|---|---|
| `/signup` | GET, POST | New customer registration with email domain validation |
| `/login` | GET, POST | Password check → triggers OTP email |
| `/otp-verify` | GET, POST | Verifies 6-digit OTP (90-second window) |
| `/logout` | GET | Clears session |
| `/forgot-password` | POST | Password reset flow |

OTP is bcrypt-hashed before storage and verified on submission. A background thread auto-expires OTPs after 90 seconds. Supported email domains include major providers plus Kenya, Nigeria, Ghana, and South Africa TLDs.

---

### Shop (`routes/shop.py`)

| Route | Description |
|---|---|
| `GET /shop` | Browse all available products |
| `GET /shop/category/<category>` | Filter products by category |
| `POST /cart/add/<product_id>` | Add item to session-based cart |
| `GET /cart` | View cart |
| `POST /checkout` | Place order |
| `GET /order-tracking/<order_id>` | Track order status |
| `GET/POST /bulk` | Place a bulk/wholesale order |
| `GET /my-bulk-orders` | View personal bulk order history |

---

### Fleet (`routes/fleet.py` + `app.py`)

| Route | Description |
|---|---|
| `GET/POST /fleetordering` | Customer submits a fleet hire request |
| `GET /fleetorders` | View orders (own for customers; all for Admin/FleetManager) |
| `GET /dashboard` | Driver/FleetManager dashboard with vehicle assignments |
| `GET/POST /vehiclesmanagefleet` | Manage vehicle assignments |
| `GET/POST /vehiclesaddnew` | Register a new vehicle |
| `GET/POST /editfleet/<fleet_id>` | Edit vehicle record |
| `GET/POST /fleetordersmanage` | Admin manages all fleet orders (approve, assign, complete) |

Fleet orders capture: cargo type, quantity, destination route, destination town, duration (auto-set to 10 days), start date, and expected return date.

---

### Gas Refill (`routes/gasrefill.py`)

| Route | Description |
|---|---|
| `GET/POST /gasrefill` | Customer requests a cylinder refill (type, size, location) |
| `GET /gasrefill/order-tracking/<id>` | Customer tracks their refill status |
| `GET/POST /gasrefill/admin` | Admin/CustomerService/Financer manages all refill requests |

Available cylinder types: Standard and Premium, in sizes 6 kg to 32 kg. Delivery locations are pre-configured Nairobi areas.

---

### Employees (`routes/employees.py`)

| Route | Description |
|---|---|
| `GET /employees` | Paginated, searchable employee list with role and status filters |
| `POST /employees/add` | Add new employee |
| `POST /employees/edit/<id>` | Edit employee record |

Admin-only. Supports filtering by role (Driver, Financer, Admin, etc.) and status (Active, On-leave, Off, Inactive), with 9 results per page.

---

### Production (`app.py`)

| Route | Description |
|---|---|
| `GET/POST /manageproduction` | View and manage product catalog |
| `GET/POST /addnewproduction` | Add product with image upload |
| `GET/POST /editproduction/<product_id>` | Edit product details |

---

### Customer Service (`app.py`)

| Route | Description |
|---|---|
| `GET/POST /customersmanage` | View and manage customer accounts |
| `GET/POST /ordersmanage` | Manage shop orders with status updates |
| `GET /vieworders` | View all orders |
| `GET /finances` | Finance dashboard (Financer role) |
| `GET /reports` | Business reports |
| `GET/POST /bulkordersmanage` | Manage all bulk orders |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip
- A Gmail account for OTP emails (or configure another SMTP provider)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/wellsflow-greenwells.git
cd wellsflow-greenwells
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask flask-login flask-sqlalchemy flask-wtf wtforms bcrypt
```

### 4. Initialize the database

```bash
cd greenwells_wellsflow
python ../dbcreation.py
```

This creates `instance/shopfleet.db` with all tables and seed data.

### 5. Run the app

```bash
python app.py
```

Navigate to `http://localhost:5000`.

---

## Configuration

Update the following before any deployment:

**`routes/auth.py` — Email/OTP config:**

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'your-email@gmail.com',      # ← Replace
    'password': 'your-app-password'       # ← Use a Gmail App Password
}
```

**`app.py` — Secret key:**

```python
app.config['SECRET_KEY'] = 'your-strong-random-secret-key'   # ← Replace
```

> **Never commit real credentials.** Use environment variables or a `.env` file with `python-dotenv`.

**Recommended environment variable setup:**

```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

---

## Authentication Flow

```
User submits email + password
          │
          ▼
  Credentials verified (bcrypt)
          │
          ▼
  6-digit OTP generated → bcrypt-hashed → stored in DB
          │
          ▼
  OTP sent via Gmail SMTP
          │
          ▼
  User submits OTP at /otp-verify
          │
          ▼
  OTP verified against stored hash (within 90s)
          │
          ▼
  Flask-Login session created
          │
          ▼
  Redirected based on role
  (Admin → dashboard | customer → shop)
```

Both `Users` (customers) and `Employees` (staff) authenticate through the same endpoint but are loaded from separate DB tables via Flask-Login's `user_loader`.

---

## Known Issues & Limitations

- **Hardcoded DB paths** — Several route files use relative paths that depend on working directory. These should be centralized using `app.config` or an environment variable.
- **OTP fixed for testing** — `generate_otp()` currently returns `"123456"`. Switch to `str(random.randint(100000, 999999))` before going live.
- **No `requirements.txt`** — Dependencies are not pinned. Add one with `pip freeze > requirements.txt`.
- **No `.env` support** — SMTP credentials and secret keys are hardcoded; move to environment variables.
- **Single SQLite file** — Suitable for development. For production traffic, migrate to PostgreSQL or MySQL.
- **No HTTPS** — Deploy behind nginx with SSL/TLS in production.

---

## Recommended `.gitignore`

```gitignore
# Database
greenwells_wellsflow/instance/*.db

# Python
__pycache__/
*.pyc
*.pyo
venv/
.env

# macOS
.DS_Store

# VS Code
.vscode/
```

---

## Author
**Collaborative effort of Stephen, Andy and George.**
Built for Petroleum products and fleet logistics companies.

---

## 📜 License

This project is proprietary. All rights reserved. Copying,cloning or duplication should not happen without my approval.
