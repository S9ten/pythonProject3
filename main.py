from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Grigoriy/PycharmProjects/pythonProject3/shop.db'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)


@app.route('/')
def index():
    items = Product.query.order_by(Product.price).all()
    return render_template('index.html', data=items)

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        product = Product(name=name, price=price)
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
