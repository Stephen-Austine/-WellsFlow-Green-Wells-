# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
import sqlite3
import bcrypt  # ✅ for password hashing

# Define the database path
shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    from forms import SignupForm  # Import here to avoid circular imports
    form = SignupForm()
    if form.validate_on_submit():
        conn = sqlite3.connect(shopfleetdb)
        cursor = conn.cursor()

        email = form.email.data.lower().strip()

        # Check if the email already exists
        cursor.execute("SELECT email FROM Users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        fname = form.fname.data.strip()
        lname = form.lname.data.strip()
        phone = form.phone.data.strip()
        password = form.password.data.strip()

        # ✅ Hash password before saving
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO Users (first_name, last_name, phone_number, email, password, location, status, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fname,
            lname,
            phone,
            email,
            hashed_password,  # store hashed password
            "Unknown",
            "Inactive",
            0
        ))

        conn.commit()
        conn.close()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect(shopfleetdb)
        cursor = conn.cursor()

        email = form.email.data.lower().strip()
        password = form.password.data

        # Check Employees first
        cursor.execute("SELECT employee_id, password, role FROM Employees WHERE email = ?", (email,))
        employee = cursor.fetchone()

        if employee:
            employee_id, stored_password, role = employee
            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                flash(f"Logged in successfully as {role}!", "success")
                conn.close()
                # ✅ Role-based redirect
                if role.lower() == "admin":
                    return redirect(url_for("fleet.fleet_home"))
                else:
                    return redirect(url_for("home"))
            else:
                flash("Invalid email or password.", "danger")
                conn.close()
                return render_template("auth/login.html", form=form)

        # If not employee, check Users table
        cursor.execute("SELECT user_id, password FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, stored_password = user
            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                flash("Logged in successfully!", "success")
                return redirect(url_for("shop.shop_home"))  # ✅ Customers go to Shop
            else:
                flash("Invalid email or password.", "danger")
        else:
            flash("Email does not exist.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
