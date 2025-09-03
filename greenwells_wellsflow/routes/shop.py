from flask import Blueprint, render_template

shop_bp = Blueprint("shop", __name__, template_folder="../templates/shop")

@shop_bp.route("/")
def shop_home():
    return "<h2>Shop System Home</h2><p>This is where customers will order products.</p>"
