from flask import Blueprint, render_template
# Define blueprint
shop_bp = Blueprint("shop", __name__)

# Shop home route
@shop_bp.route("/")
def shop_home():
    return render_template("shop.html")
