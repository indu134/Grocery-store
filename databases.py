from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database URI
db = SQLAlchemy(app)

app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)
    wallet = db.Column(db.Float,nullable=False)
    cart = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.wallet = 100

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    


class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)
    wallet = db.Column(db.Float,nullable=False)
    products = db.relationship('Product', backref='manager', lazy=True)
    api_key = db.Column(db.String(128),nullable=True)

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.wallet = 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    photo_path = db.Column(db.String(200), nullable=False)
    manager_name = db.Column(db.String(100), db.ForeignKey('manager.username'), nullable=False)




class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    photo_path = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)
    manager_name = db.Column(db.String(100),nullable=False)



class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    photo_path = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)
    manager_name = db.Column(db.String(100),nullable=False)






    


