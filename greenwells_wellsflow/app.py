from flask import Flask, render_template
from flask_login import LoginManager
from extensions import db   # from extensions.py
from routes.auth import auth_bp

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenwells_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenwells.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"  # redirect to login page

# Import models AFTER db + app are set up
from models import User

# Blueprints (import after app is defined)
from routes.shop import shop_bp
from routes.fleet import fleet_bp
from routes.auth import auth_bp   # ✅ now app is defined

# Register blueprints
app.register_blueprint(shop_bp, url_prefix="/shop")
app.register_blueprint(fleet_bp, url_prefix="/fleet")
app.register_blueprint(auth_bp, url_prefix="/auth")


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)
