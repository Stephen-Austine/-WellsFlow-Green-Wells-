from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import Product  # make sure Product model is imported

shop_bp = Blueprint('shop', __name__, url_prefix="/shop")

# --- Shop Home ---
@shop_bp.route("/")
def shop_home():
    products = Product.query.all()
    cart = session.get("cart", [])
    total_price = sum(item['price'] for item in cart)
    return render_template(
        "shop/shop_home.html",
        products=products,
        cart=cart,
        total_price=total_price
    )

# --- Add to Cart ---
@shop_bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("shop.shop_home"))

    cart = session.get("cart", [])
    cart.append({
        "id": product.product_id,
        "name": product.product_name,
        "price": product.retail_price
    })
    session["cart"] = cart
    session.modified = True

    flash(f"{product.product_name} added to cart.", "success")
    return redirect(url_for("shop.shop_home"))

# --- Remove from Cart ---
@shop_bp.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["id"] != product_id]
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("shop.shop_home"))

# --- Clear Cart ---
@shop_bp.route("/checkout", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("shop.shop_home"))

@shop_bp.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    tax = round(subtotal * 0.16, 2)  # 16% VAT example
    total = subtotal + tax

    return render_template(
        'shop/checkout.html',
        cart=cart,
        subtotal=subtotal,
        tax=tax,
        total=total
    )
