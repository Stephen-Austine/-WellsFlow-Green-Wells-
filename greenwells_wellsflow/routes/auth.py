# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
import sqlite3

# Define the database path
shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    from forms import SignupForm  # Import here to avoid circular imports
    form = SignupForm()
    if form.validate_on_submit():
        # Connect to the SQLite database
        conn = sqlite3.connect(shopfleetdb)
        cursor = conn.cursor()

        # Get the email from the form and normalize it
        email = form.email.data.lower().strip()

        # Check if the email already exists in the database
        cursor.execute("SELECT email FROM Users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Close the connection if the email already exists
            conn.close()
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        # Prepare the data for insertion
        fname = form.fname.data.strip()
        lname = form.lname.data.strip()
        phone = form.phone.data.strip()
        password = form.password.data.strip()  # Plaintext password

        # Insert the new user into the database
        cursor.execute("""
            INSERT INTO Users (first_name, last_name, phone_number, email, password, location, status, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fname,
            lname,
            phone,
            email,
            password,  # Plaintext password
            "Unknown",  # Default location
            "Inactive",  # Default status
            0  # Default last_login timestamp
        ))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        # Flash success message
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from forms import LoginForm  # Import here to avoid circular imports
    form = LoginForm()
    if form.validate_on_submit():
        # Connect to the SQLite database
        conn = sqlite3.connect(shopfleetdb)
        cursor = conn.cursor()

        # Get the email and password from the form
        email = form.email.data.lower().strip()
        password = form.password.data

        # Query the database to check if the email exists
        cursor.execute("SELECT user_id, password FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()  # Fetch the first matching row

        # Close the database connection
        conn.close()

        # Check if the email exists in the database
        if user:
            print("success")  # Print success if email exists
            user_id, stored_password = user  # Unpack the result

            # Compare plaintext passwords
            if password == stored_password:  # Plaintext comparison
                # Simulate Flask-Login behavior by fetching the user ID
                # Since we're not using SQLAlchemy, we don't have a full User object
                flash("Logged in successfully!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid email or password.", "danger")
        else:
            print("not exist")  # Print not exist if email does not exist
            flash("Email does not exist.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))