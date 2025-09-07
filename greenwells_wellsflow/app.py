from flask import Flask, render_template
from flask_login import LoginManager
import sqlite3
from user_object import UserObject

from extensions import db
from routes.shop import shop_bp
from routes.fleet import fleet_bp
from routes.auth import auth_bp

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenwells_secret'

# Use same SQLite DB for SQLAlchemy models
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopfleet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Path for raw sqlite3 queries (flask_login part)
shopfleetdb = 'instance/shopfleet.db'

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, first_name, last_name, email, 'customer' as role FROM Users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        conn.close()
        return UserObject(*row)

    cursor.execute(
        "SELECT employee_id, 'Admin', 'User', email, role FROM Employees WHERE employee_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserObject(*row)

    return None


# Register Blueprints
app.register_blueprint(shop_bp, url_prefix="/shop")
app.register_blueprint(fleet_bp, url_prefix="/fleet")
app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/dashboard")
def dashboard():
    return render_template("fleet/main_fleet_templates/dashboard.html")


@app.route("/fleet")
def fleet():
    return render_template("fleet/main_fleet_templates/fleet.html")


@app.route("/employees")
def employees():
    return render_template("fleet/main_fleet_templates/employees.html")


@app.route("/production")
def production():
    return render_template("fleet/main_fleet_templates/production.html")


@app.route("/orders")
def orders():
    return render_template("fleet/main_fleet_templates/orders.html")


@app.route("/customers")
def customers():
    return render_template("fleet/main_fleet_templates/customers.html")


@app.route("/finances")
def finances():
    return render_template("fleet/main_fleet_templates/finances.html")


@app.route("/reports")
def reports():
    return render_template("fleet/main_fleet_templates/reports.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ creates Product table if not exists
    app.run(debug=True)
