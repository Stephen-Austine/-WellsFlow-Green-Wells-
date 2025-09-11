from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import sqlite3
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import os

shop = Blueprint("shop", __name__, template_folder="../templates/shop")

# Database path
shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

def get_db_connection():
    conn = sqlite3.connect(shopfleetdb)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@shop.route('/shop')
def shop_home():
    conn = get_db_connection()
    try:
        products = conn.execute('SELECT * FROM Products WHERE status = "Not sold"').fetchall()
        categories = conn.execute('SELECT DISTINCT product_category FROM Products').fetchall()
    except sqlite3.OperationalError as e:
        flash('Database error: ' + str(e), 'danger')
        products = []
        categories = []
    finally:
        conn.close()
    
    # Use session-based cart
    cart = session.get("cart", [])
    total_price = sum(item['price'] * item.get('quantity', 1) for item in cart)
    
    return render_template('shop_home.html', products=products, categories=[c['product_category'] for c in categories], 
                         cart=cart, total_price=total_price)

@shop.route('/shop/category/<category>')
def shop_category(category):
    conn = get_db_connection()
    try:
        products = conn.execute('SELECT * FROM Products WHERE product_category = ? AND status = "Not sold"', (category,)).fetchall()
        categories = conn.execute('SELECT DISTINCT product_category FROM Products').fetchall()
    except sqlite3.OperationalError as e:
        flash('Database error: ' + str(e), 'danger')
        products = []
        categories = []
    finally:
        conn.close()
    
    # Use session-based cart
    cart = session.get("cart", [])
    total_price = sum(item['price'] * item.get('quantity', 1) for item in cart)
    
    return render_template('shop_home.html', products=products, categories=[c['product_category'] for c in categories], 
                         current_category=category, cart=cart, total_price=total_price)

@shop.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    try:
        product = conn.execute('SELECT * FROM Products WHERE product_id = ? AND status = "Not sold"', 
                             (product_id,)).fetchone()
        if product:
            # Use session cart for all users
            cart = session.get("cart", [])
            
            # Check if product already in cart
            product_found = False
            for item in cart:
                if item["id"] == product_id:
                    item["quantity"] = item.get("quantity", 1) + 1
                    product_found = True
                    break
            
            # If not found, add new item
            if not product_found:
                cart.append({
                    "id": product['product_id'],
                    "name": product['product_name'],
                    "price": product['retail_price'],
                    "quantity": 1
                })
            
            session["cart"] = cart
            session.modified = True
            flash('Product added to cart!', 'success')
        else:
            flash('Product not available.', 'danger')
    except sqlite3.OperationalError as e:
        flash('Database error: ' + str(e), 'danger')
    finally:
        conn.close()
    return redirect(url_for('shop.shop_home'))

@shop.route('/cart')
def cart():
    # Use session-based cart
    cart = session.get("cart", [])
    subtotal = sum(item['price'] * item.get('quantity', 1) for item in cart)
    tax = subtotal * 0.16  # Assuming 16% tax
    total = subtotal + tax
    
    return render_template('cart.html', cart=cart, subtotal=subtotal, tax=tax, total=total)

@shop.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    # Remove from session cart
    cart = session.get("cart", [])
    # Filter out the item with the matching ID
    new_cart = []
    for item in cart:
        if item["id"] != item_id:
            new_cart.append(item)
    session["cart"] = new_cart
    session.modified = True
    flash('Item removed from cart.', 'success')
    
    return redirect(url_for('shop.cart'))

@shop.route('/cart/clear', methods=['POST'])
def clear_cart():
    # Clear session cart
    session.pop("cart", None)
    flash('Cart cleared.', 'success')
    
    return redirect(url_for('shop.shop_home'))

@shop.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get("cart", [])
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('shop.shop_home'))
    
    if request.method == 'POST':
        # For now, just clear the cart on "checkout"
        session.pop("cart", None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('shop.shop_home'))
    
    # Display checkout page
    subtotal = sum(item['price'] * item.get('quantity', 1) for item in cart)
    tax = subtotal * 0.16
    total = subtotal + tax
    
    order = {
        'items': [{'name': item['name'], 'price': item['price'], 'quantity': item.get('quantity', 1)} for item in cart],
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }
    
    return render_template('checkout.html', order=order)


@shop.route('/order_tracking/<int:order_id>', methods = ['POST'])
def order_tracking(order_id):
    # Mock order data (later this can come from DB)
    mock_order = {
        "id": order_id,
        "customer": "John Doe",
        "items": [
            {"name": "Engine Oil", "qty": 2, "price": 1500},
            {"name": "Brake Fluid", "qty": 1, "price": 800},
        ],
        "status": "Shipped"  # Change this to test: "Placed", "Processing", "Shipped", "Delivered"
    }

    return render_template("shop/order_tracking.html", order=mock_order)
