from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Fleet, FleetOrder
from forms_fleet import FleetOrderForm

fleet_bp = Blueprint("fleet", __name__, template_folder="../templates/fleet")

@fleet_bp.route("/fleetordering", methods=["GET", "POST"])
@login_required
def fleet_home():
    # If user is an ADMIN → management dashboard
    if current_user.role == "admin":
        fleets = Fleet.query.all()
        orders = FleetOrder.query.order_by(FleetOrder.id.desc()).all()
        return render_template("fleet/admin_dashboard.html", fleets=fleets, orders=orders)

    # If user is CUSTOMER → show fleet request form
    form = FleetOrderForm()
    if form.validate_on_submit():
        order = FleetOrder(
            customer_id=current_user.id,
            vehicle_type=form.vehicle_type.data,
            quantity=form.quantity.data,
            destination=form.destination.data
        )
        db.session.add(order)
        db.session.commit()
        flash("Your fleet request has been submitted.", "success")
        return redirect(url_for("fleet.fleet_home"))

    return render_template("fleet/customer_request.html", form=form)
