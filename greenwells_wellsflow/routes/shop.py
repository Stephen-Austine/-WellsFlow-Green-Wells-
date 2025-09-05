from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

shop_bp = Blueprint("shop", __name__, template_folder="../templates/shop")

shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'


@shop_bp.route("/")
def shop_home():
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, product_description, retail_price, 'engine_oil.png' as image FROM Products")
    products = [
        {
            "product_id": row[0],
            "product_name": row[1],
            "product_description": row[2],
            "retail_price": row[3],
            "image": row[4]
        }
        for row in cursor.fetchall()
    ]
    conn.close()

    # Load cart from session
    cart = session.get("cart", [])
    subtotal = sum(item["price"] for item in cart)
    tax = round(subtotal * 0.08, 2)  # Example: 8% tax
    total = subtotal + tax

    # 🔥 Marry changes: render friend’s template if it exists, else fallback
    return render_template("shop/shop_home.html",
                           products=products,
                           cart=cart,
                           subtotal=subtotal,
                           tax=tax,
                           total=total)


@shop_bp.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    conn = sqlite3.connect(shopfleetdb)
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, retail_price FROM Products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        cart = session.get("cart", [])
        cart.append({"id": row[0], "name": row[1], "price": row[2]})
        session["cart"] = cart

    return redirect(url_for("shop.shop_home"))
