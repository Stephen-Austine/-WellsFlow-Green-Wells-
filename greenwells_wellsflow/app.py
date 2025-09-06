from flask import *
from flask_login import LoginManager, login_required
import sqlite3
from user_object import UserObject

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenwells_secret'

# Path to your actual SQLite database
shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # First check Users table
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, 'customer' as role FROM Users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        print(f"Loading User from session: {row['first_name']} {row['last_name']} (ID: {row['user_id']})")  # Debug line
        conn.close()
        return UserObject(row['user_id'], row['first_name'], row['last_name'], row['email'], row['role'])

    # If not found, check Employees table
    cursor.execute(
        "SELECT employee_id, first_name, last_name, email, role, username FROM Employees WHERE employee_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        print(f"Loading Employee from session: {row['first_name']} {row['last_name']} - Username: {row['username']} (ID: {row['employee_id']})")  # Debug line
        return UserObject(row['employee_id'], row['first_name'], row['last_name'], row['email'], row['role'], row['username'])

    print(f"No user found for ID: {user_id}")  # Debug line
    return None

# Blueprints
from routes.shop import shop_bp
from routes.fleet import fleet_bp
from routes.auth import auth_bp

app.register_blueprint(shop_bp, url_prefix="/shop")
app.register_blueprint(fleet_bp, url_prefix="/fleet")
app.register_blueprint(auth_bp, url_prefix="/auth")

# Debug route to check registered routes
@app.route("/debug-routes")
def debug_routes():
    from flask import url_for
    try:
        routes = {
            'auth.login': url_for('auth.login'),
            'auth.signup': url_for('auth.signup'),
            'auth.test': url_for('auth.test')
        }
        return f"<pre>{routes}</pre>"
    except Exception as e:
        return f"Error: {str(e)}"

# ... rest of your routes


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/debug-all-users")
def debug_all_users():
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()
    
    result = "<h2>Database Users Debug</h2>"
    
    # Check Users table
    cursor.execute("SELECT user_id, first_name, last_name, email FROM Users")
    users = cursor.fetchall()
    result += "<h3>Users Table:</h3><ul>"
    for user in users:
        result += f"<li>ID: {user[0]}, Name: {user[1]} {user[2]}, Email: {user[3]}</li>"
    result += "</ul>"
    
    # Check Employees table
    cursor.execute("SELECT employee_id, first_name, last_name, username, email, role FROM Employees")
    employees = cursor.fetchall()
    result += "<h3>Employees Table:</h3><ul>"
    for emp in employees:
        result += f"<li>ID: {emp[0]}, Name: {emp[1]} {emp[2]}, Username: {emp[3]}, Email: {emp[4]}, Role: {emp[5]}</li>"
    result += "</ul>"
    
    conn.close()
    return result


@app.route("/dashboard")
def dashboard():
    return render_template("fleet/adminside_fleet/dashboard.html")


@app.route("/vehicles")
def vehicles():
    return render_template("fleet/adminside_fleet/vehicles.html")


@app.route("/vehiclesmanagefleet", methods=['GET', 'POST'])
@login_required
def vehiclesmanagefleet():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get the filter status from query parameters
    filter_status = request.args.get('status')
    
    # Handle status update
    if request.method == 'POST':
        fleet_id = request.form.get('fleet_id')
        new_status = request.form.get('status')
        
        cursor.execute("UPDATE Fleet SET status = ? WHERE fleet_id = ?", (new_status, fleet_id))
        conn.commit()
        flash("Fleet status updated successfully!", "success")
        # Preserve filter after update
        redirect_url = url_for('vehiclesmanagefleet')
        if filter_status:
            redirect_url += f'?status={filter_status}'
        return redirect(redirect_url)
    
    # Fetch filtered or all fleets
    if filter_status:
        cursor.execute("SELECT * FROM Fleet WHERE status = ?", (filter_status,))
    else:
        cursor.execute("SELECT * FROM Fleet")
    fleets = cursor.fetchall()
    
    # Get status counts for navbar
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM Fleet 
        GROUP BY status
    """)
    status_counts = cursor.fetchall()
    
    conn.close()
    
    return render_template("fleet/fleet_extend/vehicles/managefleet.html", 
                         fleets=fleets, 
                         status_counts=status_counts,
                         current_filter=filter_status)


@app.route("/employees")
def employees():
    return render_template("fleet/adminside_fleet/employees.html")


@app.route("/production")
def production():
    return render_template("fleet/adminside_fleet/production.html")


@app.route("/orders")
def orders():
    return render_template("fleet/adminside_fleet/orders.html")


@app.route("/customers")
def customers():
    return render_template("fleet/adminside_fleet/customers.html")


@app.route("/finances")
def finances():
    return render_template("fleet/adminside_fleet/finances.html")

@app.route("/reports")
def reports():
    return render_template("fleet/adminside_fleet/reports.html")


if __name__ == "__main__":
    app.run(debug=True)
