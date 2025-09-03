# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models import User
from forms import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # prevent duplicate email
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            fname=form.fname.data.strip(),
            lname=form.lname.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
