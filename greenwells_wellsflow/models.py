from flask_login import UserMixin
import bcrypt
from extensions import db   # ✅ no circular import

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), default="customer")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    status = db.Column(db.String(50), default="Received")

