from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
import sqlite3
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime

shop = Blueprint("shop", __name__, template_folder="../templates/shop")

def get_db_connection():
    conn = sqlite3.connect('../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db')
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    return conn

shopfleetdb = '../-WellsFlow-Green-Wells-/greenwells_wellsflow/instance/shopfleet.db'

# Forms
class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('Add to Cart')

class CheckoutForm(FlaskForm):
    destination = StringField('Delivery Address', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[('mpesa', 'M-Pesa')], validators=[DataRequired()])
    submit = SubmitField('Place Order')

# Routes
@shop.route('/shop')
def shop_home():
    conn = get_db_connection()
    try:
        products = conn.execute('SELECT * FROM Products WHERE status = "Not sold"').fetchall()
        categories = conn.execute('SELECT DISTINCT product_category FROM Products').fetchall()
    except sqlite3.OperationalError as e:
        flash('Database error: Table Products not found. Please initialize the database.', 'danger')
        products = []
        categories = []
    finally:
        conn.close()
    
    cart = []
    total_price = 0
    if current_user.is_authenticated:
        conn = get_db_connection()
        try:
            cart_items = conn.execute(
                'SELECT c.cart_id, p.product_name, p.retail_price, c.status '
                'FROM Cart c JOIN Products p ON c.product_id = p.product_id '
                'WHERE c.user_id = ? AND c.status = "Wishlist"', 
                (current_user.user_id,)
            ).fetchall()
            cart = [{'cart_id': item['cart_id'], 'name': item['product_name'], 'price': item['retail_price']} for item in cart_items]
            total_price = sum(item['price'] for item in cart)
        except sqlite3.OperationalError:
            flash('Database error: Unable to load cart.', 'danger')
        finally:
            conn.close()
    
    return render_template('shop_home.html', products=products, categories=[c['product_category'] for c in categories], 
                         cart=cart, total_price=total_price)

@shop.route('/shop/category/<category>')
def shop_category(category):
    conn = get_db_connection()
    try:
        products = conn.execute('SELECT * FROM Products WHERE product_category = ? AND status = "Not sold"', (category,)).fetchall()
        categories = conn.execute('SELECT DISTINCT product_category FROM Products').fetchall()
    except sqlite3.OperationalError as e:
        flash('Database error: Table Products not found.', 'danger')
        products = []
        categories = []
    finally:
        conn.close()
    
    return render_template('shop.html', products=products, categories=[c['product_category'] for c in categories], 
                         current_category=category)

@shop.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    form = AddToCartForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        try:
            product = conn.execute('SELECT * FROM Products WHERE product_id = ? AND status = "Not sold"', 
                                 (product_id,)).fetchone()
            if product:
                if product['product_quantity'] >= form.quantity.data:
                    conn.execute(
                        'INSERT INTO Cart (product_id, user_id, status) VALUES (?, ?, ?)',
                        (product_id, current_user.user_id, 'Wishlist')
                    )
                    conn.commit()
                    flash('Product added to cart!', 'success')
                else:
                    flash('Insufficient stock available.', 'danger')
            else:
                flash('Product not available.', 'danger')
        except sqlite3.OperationalError:
            flash('Database error: Unable to add to cart.', 'danger')
        finally:
            conn.close()
    return redirect(url_for('shop.shop_home'))

@shop.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    try:
        cart_items = conn.execute(
            'SELECT c.cart_id, p.product_name, p.retail_price, c.status '
            'FROM Cart c JOIN Products p ON c.product_id = p.product_id '
            'WHERE c.user_id = ? AND c.status = "Wishlist"', 
            (current_user.user_id,)
        ).fetchall()
    except sqlite3.OperationalError:
        flash('Database error: Unable to load cart.', 'danger')
        cart_items = []
    finally:
        conn.close()
    
    cart = [{'cart_id': item['cart_id'], 'name': item['product_name'], 'price': item['retail_price'], 'qty': 1} for item in cart_items]
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    tax = subtotal * 0.16  # Assuming 16% tax
    total = subtotal + tax
    
    return render_template('cart.html', cart=cart, subtotal=subtotal, tax=tax, total=total)

@shop.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Cart WHERE cart_id = ? AND user_id = ?', (cart_id, current_user.user_id))
        conn.commit()
        flash('Item removed from cart.', 'success')
    except sqlite3.OperationalError:
        flash('Database error: Unable to remove from cart.', 'danger')
    finally:
        conn.close()
    return redirect(url_for('shop.cart'))

@shop.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        try:
            cart_items = conn.execute(
                'SELECT c.cart_id, c.product_id, p.retail_price '
                'FROM Cart c JOIN Products p ON c.product_id = p.product_id '
                'WHERE c.user_id = ? AND c.status = "Wishlist"', 
                (current_user.user_id,)
            ).fetchall()
            
            if not cart_items:
                flash('Your cart is empty.', 'danger')
                conn.close()
                return redirect(url_for('shop.cart'))
            
            # Create order
            for item in cart_items:
                conn.execute(
                    'INSERT INTO Orders (product_id, user_id, employee_id, fleet_id, status, order_timestamp) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (item['product_id'], current_user.user_id, 0, 0, 'Stage 1', datetime.now().timestamp())
                )
                conn.execute('UPDATE Cart SET status = "Ordered" WHERE cart_id = ?', (item['cart_id'],))
                conn.execute('UPDATE Products SET product_quantity = product_quantity - 1 WHERE product_id = ?', 
                            (item['product_id'],))
            
            conn.commit()
            flash('Order placed successfully! Payment processing via M-Pesa.', 'success')
            return redirect(url_for('shop.order_confirmation'))
        except sqlite3.OperationalError as e:
            flash(f'Database error: {str(e)}', 'danger')
        finally:
            conn.close()
    
    conn = get_db_connection()
    try:
        cart_items = conn.execute(
            'SELECT p.product_name, p.retail_price '
            'FROM Cart c JOIN Products p ON c.product_id = p.product_id '
            'WHERE c.user_id = ? AND c.status = "Wishlist"', 
            (current_user.user_id,)
        ).fetchall()
    except sqlite3.OperationalError:
        flash('Database error: Unable to load cart for checkout.', 'danger')
        cart_items = []
    finally:
        conn.close()
    
    order = {
        'items': [{'name': item['product_name'], 'price': item['retail_price'], 'quantity': 1} for item in cart_items],
        'subtotal': sum(item['retail_price'] for item in cart_items),
        'tax': sum(item['retail_price'] for item in cart_items) * 0.16,
    }
    order['total'] = order['subtotal'] + order['tax']
    
    return render_template('checkout.html', form=form, order=order)

@shop.route('/order/confirmation')
@login_required
def order_confirmation():
    conn = get_db_connection()
    try:
        orders = conn.execute(
            'SELECT o.order_id, p.product_name, o.status, o.order_timestamp '
            'FROM Orders o JOIN Products p ON o.product_id = p.product_id '
            'WHERE o.user_id = ?', 
            (current_user.user_id,)
        ).fetchall()
    except sqlite3.OperationalError:
        flash('Database error: Unable to load orders.', 'danger')
        orders = []
    finally:
        conn.close()
    
    return render_template('checkout.html', order={
        'items': [{'name': o['product_name'], 'quantity': 1, 'price': 0} for o in orders],  # Price not stored in Orders
        'subtotal': 0,  # Placeholder
        'tax': 0,
        'total': 0
    })

@shop.route('/order/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    conn = get_db_connection()
    try:
        order = conn.execute('SELECT status, product_id FROM Orders WHERE order_id = ? AND user_id = ?', 
                            (order_id, current_user.user_id)).fetchone()
        
        if not order:
            flash('Order not found.', 'danger')
            conn.close()
            return redirect(url_for('shop.order_confirmation'))
        
        if order['status'] in ['Stage 1', 'Stage 2']:
            conn.execute('UPDATE Orders SET status = "Cancelled" WHERE order_id = ?', (order_id,))
            conn.execute('UPDATE Products SET product_quantity = product_quantity + 1 WHERE product_id = ?', 
                        (order['product_id'],))
            conn.commit()
            flash('Order cancelled successfully.', 'success')
        else:
            flash('Order cannot be cancelled at this stage. Contact support.', 'danger')
    except sqlite3.OperationalError:
        flash('Database error: Unable to cancel order.', 'danger')
    finally:
        conn.close()
    return redirect(url_for('shop.order_confirmation'))