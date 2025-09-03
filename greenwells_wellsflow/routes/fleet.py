# routes/fleet.py
from flask import Blueprint
from utils import admin_required

fleet_bp = Blueprint("fleet", __name__, template_folder="../templates/fleet")

@fleet_bp.route("/")
@admin_required
def fleet_home():
    return "<h2>Fleet Management Home</h2><p>Admins only.</p>"
