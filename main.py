from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Grigoriy/PycharmProjects/pythonProject3/shop.db'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100))
    # photo = ???


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False)
    dealer_id = db.Column(db.String(30))
    date = db.Column(db.DateTime)
    password = db.Column(db.String(100), nullable=False)
    adress = db.Column(db.String(100))


@app.route('/', methods=["GET", "POST"])
def index():
    items = Product.query.order_by(Product.price).all()
    if request.method == "POST":
        return redirect('/')
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/registr', methods=["GET", "POST"])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        dealer_id = request.form['dealer_id']
        email = request.form['email']
        # не защищен!!!!!!!!!!!!
        password = request.form['password']
        adress = request.form['adress']
        user = User(name=name, dealer_id=dealer_id, email=email, password=password, adress=adress)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR'
    else:
        return render_template('create_profile.html')


@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        product = Product(name=name, price=price, description=description)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR'
    else:
        return render_template('create.html')


if __name__ == '__main__':
    app.run()
