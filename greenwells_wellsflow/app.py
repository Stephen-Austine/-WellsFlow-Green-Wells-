from flask import Flask, render_template
from flask_login import LoginManager
import sqlite3
from user_object import UserObject

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenwells_secret'

# Path to your actual SQLite database
shopfleetdb = 'instance/shopfleet.db'

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"  # redirect if not logged in


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()

    # First check Users table
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, 'customer' as role FROM Users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        conn.close()
        return UserObject(*row)

    # If not found, check Employees table
    cursor.execute(
        "SELECT employee_id, 'Admin', 'User', email, role FROM Employees WHERE employee_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserObject(*row)

    return None


# Blueprints
from routes.shop import shop_bp
from routes.fleet import fleet_bp
from routes.auth import auth_bp

app.register_blueprint(shop_bp, url_prefix="/shop")
app.register_blueprint(fleet_bp, url_prefix="/fleet")
app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/dashboard")
def dashboard():
    return render_template("fleet/dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
