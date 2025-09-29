from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
import sqlite3
from user_object import UserObject
from routes import register_blueprints  # ✅ auto-blueprint loader
from functools import wraps

# Add the role_required decorator
def role_required(allowed_roles):
    """
    Decorator to check if the current user has the required role
    allowed_roles: list of allowed roles or a single role string
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not hasattr(current_user, 'role'):
                flash('Access denied: Role information not available.', 'danger')
                return redirect(url_for('home'))
            
            user_role = current_user.role
            
            # Convert single role to list for consistent checking
            roles_to_check = allowed_roles if isinstance(allowed_roles, list) else [allowed_roles]
            
            if user_role not in roles_to_check:
                flash(f'Access denied: You need {", ".join(roles_to_check)} role(s) to access this page.', 'danger')
                
                # Redirect based on user's role to avoid infinite loops
                role = user_role.lower()
                if role == "admin":
                    return redirect(url_for("dashboard"))
                elif role in ["FleetManager", "Driver"]:
                    return redirect(url_for("vehiclesmanagefleet"))
                elif role == "Productmanager":
                    return redirect(url_for("manageproduction"))
                elif role == "Customerservice":
                    return redirect(url_for("customersmanage"))
                elif role == "Financer":
                    return redirect(url_for("finances"))
                else:
                    # Default redirect for unknown roles or customer
                    return redirect(url_for("home"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenwells_secret'

# Path to your actual SQLite database
shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"  # redirect if not logged in


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, first_name, last_name, email, 'customer' as role FROM Users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        conn.close()
        return UserObject(row['user_id'], row['first_name'], row['last_name'], row['email'], row['role'])

    cursor.execute(
        "SELECT employee_id, first_name, last_name, email, role FROM Employees WHERE employee_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserObject(row['employee_id'], row['first_name'], row['last_name'], row['email'], row['role'])

    return None


#  Auto-register all Blueprints from routes/
register_blueprints(app)


@app.route("/debug-routes")
def debug_routes():
    try:
        routes = {
            'auth.login': url_for('auth.login'),
            'auth.signup': url_for('auth.signup'),
            'auth.test': url_for('auth.test')
        }
        return f"<pre>{routes}</pre>"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/debug-all-users")
def debug_all_users():
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()

    result = "<h2>Database Users Debug</h2>"

    cursor.execute("SELECT user_id, first_name, last_name, email FROM Users")
    users = cursor.fetchall()
    result += "<h3>Users Table:</h3><ul>"
    for user in users:
        result += f"<li>ID: {user[0]}, Name: {user[1]} {user[2]}, Email: {user[3]}</li>"
    result += "</ul>"

    cursor.execute("SELECT employee_id, first_name, last_name, email, role FROM Employees")
    employees = cursor.fetchall()
    result += "<h3>Employees Table:</h3><ul>"
    for emp in employees:
        result += f"<li>ID: {emp[0]}, Name: {emp[1]} {emp[2]}, Email: {emp[3]}, Role: {emp[4]}</li>"
    result += "</ul>"

    conn.close()
    return result


@app.route("/dashboard")
def dashboard():
    return render_template("fleet/adminside_fleet/dashboard.html")


@app.route("/vehicles")
@role_required(['FleetManager', 'Admin', 'Driver'])
def vehicles():
    return render_template("fleet/adminside_fleet/vehicles.html")


# Updated route in app.py
@app.route("/vehiclesmanagefleet", methods=['GET', 'POST'])
@role_required(['FleetManager', 'Admin', 'Driver'])
def vehiclesmanagefleet():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    filter_status = request.args.get('status')

    if request.method == 'POST':
        fleet_id = request.form.get('fleet_id')
        new_status = request.form.get('status')

        cursor.execute("UPDATE Fleet SET status = ? WHERE fleet_id = ?", (new_status, fleet_id))
        conn.commit()
        flash("Fleet status updated successfully!", "success")

        redirect_url = url_for('vehiclesmanagefleet')
        if filter_status:
            redirect_url += f'?status={filter_status}'
        return redirect(redirect_url)

    if filter_status:
        cursor.execute("SELECT * FROM Fleet WHERE status = ?", (filter_status,))
    else:
        cursor.execute("SELECT * FROM Fleet")
    fleets = cursor.fetchall()

    # Get status counts
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM Fleet 
        GROUP BY status
    """)
    status_counts = cursor.fetchall()

    # Get total fleet count
    cursor.execute("SELECT COUNT(*) as total FROM Fleet")
    total_fleets = cursor.fetchone()['total']

    conn.close()

    return render_template("fleet/fleet_extend/vehicles/managefleet.html",
                           fleets=fleets,
                           status_counts=status_counts,
                           current_filter=filter_status,
                           total_fleets=total_fleets)


# Updated route in app.py
@app.route("/vehiclesaddnew", methods=['GET', 'POST'])
@role_required(['FleetManager', 'Admin'])
def vehiclesaddnew():
    if request.method == 'POST':
        # Get form data
        registration_number = request.form.get('registration_number')
        fleet_brand = request.form.get('fleet_brand')
        fleet_model = request.form.get('fleet_model')
        fleet_category = request.form.get('fleet_category')
        registration_date = request.form.get('registration_date')
        fleet_mileage = request.form.get('fleet_mileage')
        chassis_number = request.form.get('chassis_number')
        cargo_type = request.form.get('cargo_type')
        max_capacity = request.form.get('max_capacity')
        
        # Default values as per your requirements
        status = 'Idle'  # Default status is Idle
        
        # Get the current logged-in user's ID
        # Based on your load_user function, the ID is stored in user_id for Users 
        # and employee_id for Employees
        employee_id = getattr(current_user, 'id', None) or getattr(current_user, 'user_id', None)
        
        # If we still don't have an employee_id, check if it's an employee
        if not employee_id:
            # Check if the current user has an employee_id attribute (from Employees table)
            employee_id = getattr(current_user, 'employee_id', None)
        
        # If we still can't find it, we might need to handle this case
        if not employee_id:
            flash("Unable to determine employee ID. Please contact administrator.", "danger")
            return redirect(url_for('vehiclesaddnew'))
        
        try:
            conn = sqlite3.connect(shopfleetdb)
            cursor = conn.cursor()
            
            # Insert new vehicle into Fleet table
            cursor.execute("""
                INSERT INTO Fleet (
                    registration_number, fleet_brand, fleet_model, fleet_category,
                    registration_date, employee_id, fleet_mileage, chassis_number,
                    cargo_type, max_capacity, status, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                registration_number, fleet_brand, fleet_model, fleet_category,
                registration_date, employee_id, fleet_mileage, chassis_number,
                cargo_type, max_capacity, status, 0
            ))
            
            conn.commit()
            conn.close()
            
            flash("Vehicle added successfully!", "success")
            return redirect(url_for('vehiclesmanagefleet'))
            
        except Exception as e:
            flash(f"Error adding vehicle: {str(e)}", "danger")
            return redirect(url_for('vehiclesaddnew'))
    
    # For GET request, no need to fetch employees since it's auto-assigned
    return render_template("fleet/fleet_extend/vehicles/addnew.html")


# Updated route in app.py
@app.route("/manageproduction", methods=['GET', 'POST'])
@role_required(['ProductManager', 'Admin'])
def manageproduction():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    filter_category = request.args.get('category')
    filter_status = request.args.get('status')

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        new_status = request.form.get('status')

        cursor.execute("UPDATE Products SET status = ? WHERE product_id = ?", (new_status, product_id))
        conn.commit()
        flash("Product status updated successfully!", "success")

        redirect_url = url_for('manageproduction')
        if filter_category:
            redirect_url += f'?category={filter_category}'
        elif filter_status:
            redirect_url += f'?status={filter_status}'
        return redirect(redirect_url)

    # Build query based on filters
    query = "SELECT p.*, u.first_name, u.last_name FROM Products p LEFT JOIN Users u ON p.user_id = u.user_id"
    params = []
    
    if filter_category:
        query += " WHERE p.product_category = ?"
        params.append(filter_category)
    elif filter_status:
        query += " WHERE p.status = ?"
        params.append(filter_status)
    
    query += " ORDER BY p.product_registration DESC"
    
    cursor.execute(query, params)
    products = cursor.fetchall()

    # Get category counts
    cursor.execute("""
        SELECT product_category, COUNT(*) as count 
        FROM Products 
        GROUP BY product_category
    """)
    category_counts = cursor.fetchall()
    
    # Get status counts
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM Products 
        GROUP BY status
    """)
    status_counts = cursor.fetchall()

    # Get total product count
    cursor.execute("SELECT COUNT(*) as total FROM Products")
    total_products = cursor.fetchone()['total']

    conn.close()

    return render_template("fleet/fleet_extend/production/manageproduction.html",
                           products=products,
                           category_counts=category_counts,
                           status_counts=status_counts,
                           current_category=filter_category,
                           current_status=filter_status,
                           total_products=total_products)


import os
import datetime
from werkzeug.utils import secure_filename

# Add configuration for file uploads
UPLOAD_FOLDER = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

# Make sure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Update this part in your addnewproduction route
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/addnewproduction", methods=['GET', 'POST'])
@role_required(['ProductManager', 'Admin'])
def addnewproduction():
    # Update the upload folder path
    UPLOAD_FOLDER = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

    # Make sure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if request.method == 'POST':
        # Get form data
        product_name = request.form.get('product_name')
        product_category = request.form.get('product_category')
        product_description = request.form.get('product_description')
        product_quantity = request.form.get('product_quantity')
        product_cost = request.form.get('product_cost')
        retail_price = request.form.get('retail_price')
        product_location = request.form.get('product_location')
        location_description = request.form.get('location_description', '')
        
        # Handle file upload
        product_image_filename = ''
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
                unique_filename = timestamp + filename
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                # Store just the filename
                product_image_filename = unique_filename
        
        # Default values
        status = 'In Stock'  # Default status is In Stock
        product_registration = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get the current logged-in user's ID
        user_id = getattr(current_user, 'id', None)
        if not user_id:
            for attr in ['user_id', 'employee_id', 'id']:
                if hasattr(current_user, attr):
                    user_id = getattr(current_user, attr)
                    break
        
        if not user_id:
            flash("Unable to determine your user ID. Access denied.", "danger")
            return redirect(url_for('addnewproduction'))
        
        try:
            conn = sqlite3.connect(shopfleetdb)
            cursor = conn.cursor()
            
            # Insert new product into Products table
            cursor.execute("""
                INSERT INTO Products (
                    product_name, product_category, product_description, product_image,
                    product_quantity, product_cost, retail_price, user_id,
                    product_registration, product_location, location_description, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_name, product_category, product_description, product_image_filename,
                product_quantity, product_cost, retail_price, user_id,
                product_registration, product_location, location_description, status
            ))
            
            conn.commit()
            conn.close()
            
            flash("Product added successfully!", "success")
            return redirect(url_for('manageproduction'))
            
        except Exception as e:
            flash(f"Error adding product: {str(e)}", "danger")
            return redirect(url_for('addnewproduction'))
    
    # For GET request
    return render_template("fleet/fleet_extend/production/addnewproduction.html")


@app.route("/employees")
@role_required(['Admin'])
def employees():
    return render_template("fleet/adminside_fleet/employees/employees.html")


@app.route("/orders")
@role_required(['CustomerService', 'Admin', 'Financer'])
def orders():
    return render_template("fleet/adminside_fleet/orders.html")


# Add this route to your app.py
@app.route("/customersmanage", methods=['GET', 'POST'])
@role_required(['CustomerService', 'Admin'])
def customersmanage():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    filter_status = request.args.get('status')

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_status = request.form.get('status')

        cursor.execute("UPDATE Users SET status = ? WHERE user_id = ?", (new_status, user_id))
        conn.commit()
        flash("Customer status updated successfully!", "success")

        redirect_url = url_for('customersmanage')
        if filter_status:
            redirect_url += f'?status={filter_status}'
        return redirect(redirect_url)

    if filter_status:
        cursor.execute("SELECT * FROM Users WHERE status = ?", (filter_status,))
    else:
        cursor.execute("SELECT * FROM Users")
    customers = cursor.fetchall()

    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM Users 
        GROUP BY status
    """)
    status_counts = cursor.fetchall()

    # Get total customer count
    cursor.execute("SELECT COUNT(*) as total FROM Users")
    total_customers = cursor.fetchone()['total']

    conn.close()

    return render_template("fleet/fleet_extend/customers/managecustomers.html",
                           customers=customers,
                           status_counts=status_counts,
                           current_filter=filter_status,
                           total_customers=total_customers)


@app.route("/ordersmanage", methods=['GET', 'POST'])
@role_required(['CustomerService', 'Admin', 'Financer'])
def ordersmanage():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    filter_status = request.args.get('status')

    if request.method == 'POST':
        order_id = request.form.get('order_id')
        new_status = request.form.get('status')

        cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        conn.commit()
        flash("Order status updated successfully!", "success")

        redirect_url = url_for('ordersmanage')
        if filter_status:
            redirect_url += f'?status={filter_status}'
        return redirect(redirect_url)

    # Fetch orders with related information
    if filter_status:
        cursor.execute("""
            SELECT o.*, 
                   u.first_name as customer_first_name, 
                   u.last_name as customer_last_name,
                   u.email as customer_email,
                   u.location as customer_location,
                   e.first_name as employee_first_name, 
                   e.last_name as employee_last_name,
                   f.registration_number as fleet_registration,
                   c.status as cart_status
            FROM Orders o
            LEFT JOIN Cart c ON o.cart_id = c.cart_id
            LEFT JOIN Users u ON c.user_id = u.user_id
            LEFT JOIN Employees e ON o.employee_id = e.employee_id
            LEFT JOIN Fleet f ON o.fleet_id = f.fleet_id
            WHERE o.status = ?
            ORDER BY o.order_timestamp DESC
        """, (filter_status,))
    else:
        cursor.execute("""
            SELECT o.*, 
                   u.first_name as customer_first_name, 
                   u.last_name as customer_last_name,
                   u.email as customer_email,
                   u.location as customer_location,
                   e.first_name as employee_first_name, 
                   e.last_name as employee_last_name,
                   f.registration_number as fleet_registration,
                   c.status as cart_status
            FROM Orders o
            LEFT JOIN Cart c ON o.cart_id = c.cart_id
            LEFT JOIN Users u ON c.user_id = u.user_id
            LEFT JOIN Employees e ON o.employee_id = e.employee_id
            LEFT JOIN Fleet f ON o.fleet_id = f.fleet_id
            ORDER BY o.order_timestamp DESC
        """)
    
    orders = cursor.fetchall()

    # Process orders to extract detailed cart information
    processed_orders = []
    for order in orders:
        order_dict = dict(order)
        
        # Parse cart items from cart status (where we stored the detailed info)
        cart_status = order_dict.get('cart_status', '')
        parsed_items = []
        
        # Extract cart items from cart status
        if 'Order_Items:' in cart_status:
            try:
                cart_details_str = cart_status.split('Order_Items:')[1]
                items = cart_details_str.split('; ')
                for item in items:
                    # Parse: "Product Name (ID: 123) x2 - Location: Warehouse A"
                    parsed_item = {
                        'name': 'Unknown',
                        'id': 'Unknown',
                        'quantity': '1',
                        'location': 'Unknown'
                    }
                    
                    try:
                        # Extract name
                        if ' (ID: ' in item:
                            name_part = item.split(' (ID: ')[0]
                            parsed_item['name'] = name_part
                        
                        # Extract ID
                        if ' (ID: ' in item and ') x' in item:
                            id_part = item.split(' (ID: ')[1].split(') x')[0]
                            parsed_item['id'] = id_part
                        
                        # Extract quantity and location
                        if ') x' in item and ' - Location: ' in item:
                            qty_loc_part = item.split(') x')[1]
                            if ' - Location: ' in qty_loc_part:
                                qty_part = qty_loc_part.split(' - Location: ')[0]
                                loc_part = qty_loc_part.split(' - Location: ')[1]
                                parsed_item['quantity'] = qty_part
                                parsed_item['location'] = loc_part
                            else:
                                parsed_item['quantity'] = qty_loc_part
                    except:
                        # If parsing fails, use the raw item
                        parsed_item['name'] = item
                    
                    parsed_items.append(parsed_item)
            except:
                pass
        
        order_dict['parsed_items'] = parsed_items
        processed_orders.append(order_dict)

    # Get status counts
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM Orders 
        GROUP BY status
    """)
    status_counts = cursor.fetchall()

    # Get total orders count
    cursor.execute("SELECT COUNT(*) as total FROM Orders")
    total_orders = cursor.fetchone()['total']

    conn.close()

    return render_template("fleet/fleet_extend/orders/manageorders.html",
                           orders=processed_orders,
                           status_counts=status_counts,
                           current_filter=filter_status,
                           total_orders=total_orders)


@app.route("/finances")
@role_required(['Financer', 'Admin'])
def finances():
    return render_template("fleet/adminside_fleet/finances.html")


@app.route("/reports")
@role_required(['Admin', 'Financer', 'ProductManager'])
def reports():
    return render_template("fleet/adminside_fleet/reports.html")


if __name__ == '__main__':
    app.run(debug=True)