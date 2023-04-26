from flask import Flask, url_for, request, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from data.category import Category
from data.cart import Cart
from data import db_session
from data.products import Product
from data.users import User
from forms.login_forms import LoginForm
from forms.product import ProductForm
from forms.user import RegisterForm, UserEditForm
from img_reverse import byte_img_to_html


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Product)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@app.route('/grid', methods=['GET', 'POST'])
def index2():
    db_sess = db_session.create_session()
    products = db_sess.query(Product)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index2.html', title='Товары', products=lst)


@app.route('/sort_price', methods=['GET', 'POST'])
def sort_price():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@app.route('/sort_date', methods=['GET', 'POST'])
def sort_date():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.modified_date)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@app.route('/sort_price_min', methods=['GET', 'POST'])
def sort_price_min():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price.desc())
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@app.route('/sort_date_min', methods=['GET', 'POST'])
def sort_date_min():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.modified_date.desc())
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/registr', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('create_profile.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('create_profile.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            address=form.address.data,
            is_admin=form.is_admin.data,
            dealer_id=form.dealer_id.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
    return render_template('create_profile.html', title='Регистрация', form=form)


@app.route('/user/ed/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = UserEditForm()
    db_sess = db_session.create_session()
    if request.method == "GET":
        if current_user.id == user_id or current_user.is_admin:
            user = db_sess.query(User).filter(User.id == user_id).first()
            if user:
                form.email.data = user.email
                form.name.data = user.name
                form.surname.data = user.surname
                form.age.data = user.age
                form.address.data = user.address
                form.is_admin.data = user.is_admin
                form.dealer_id.data = user.dealer_id
            else:
                abort(404)
        else:
            abort(404)
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user:
            user.email = form.email.data
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            user.address = form.address.data
            user.is_admin = form.is_admin.data
            user.dealer_id = form.dealer_id.data
            if form.password.data:
                user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('create_profile.html', edit=True, title='Редактирование', form=form)


@app.route('/user/<string:user_id>', methods=['GET', 'POST'])
# @login_required
def user(user_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.id == user_id) | (User.dealer_id == user_id)).first()
        products = db_sess.query(Product).filter(Product.manufacturer_id == user_id)
        lst = []
        for i in products:
            s = []
            for j in i.categories:
                s.append(j.name)
            lst.append((i, ' '.join(s)))
        return render_template('user.html', title='Страница', user=user, products=lst)
    else:
        return redirect('/login')


@app.route('/profile_list')
@login_required
def profile_list():
    db_sess = db_session.create_session()
    if current_user.is_moder:
        profiles = db_sess.query(User).all()
        lst = []
        for i in profiles:
            lst.append(i)
        return render_template('profiles.html', title='Profiles', profiles=lst)
    return redirect('/')


@app.route('/delete_dealer/<string:dealer_id>')
@login_required
def delete_dealer(dealer_id):
    db_sess = db_session.create_session()
    if current_user.is_moder:
        profile = db_sess.query(User).filter(User.dealer_id == dealer_id).first()
        product = db_sess.query(Product).filter(Product.manufacturer_id == dealer_id).first()
        db_sess.delete(product)
        db_sess.delete(profile)
        db_sess.commit()
        return redirect('/profile_list')
    return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = ProductForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    if form.validate_on_submit():
        product = Product()
        product.title = form.title.data
        product.price = form.price.data
        product.numb = form.numb.data
        product.about = form.about.data
        product.categories.extend(
            db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
        # current_user.news.append(news)
        # db_sess.merge(current_user)
        if request.files['file']:
            product.image = byte_img_to_html(request.files['file'])
        product.manufacturer = current_user
        db_sess.merge(product)

        db_sess.commit()
        return redirect('/')
    return render_template('create.html', title='Добавление продукта',
                           form=form)


# @app.route('/product_delete/<int:product_id>', methods=['GET', 'POST'])
# @login_required
# def product_delete(product_id):
#     db_sess = db_session.create_session()
#     if current_user.is_admin:
#         product = db_sess.query(Product).filter(Product.id == product_id,
#                                                 Product.manufacturer == current_user).first()
#     else:
#         product = None
#     if product:
#         db_sess.delete(product)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/')


@app.route('/delete/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete(product_id):
    db_sess = db_session.create_session()
    if current_user.is_admin:
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        db_sess.delete(product)
        db_sess.commit()
    return redirect('/')


@app.route('/delete_cart/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_cart(product_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        product = db_sess.query(Cart).filter(Cart.id == product_id).first()
        db_sess.delete(product)
        db_sess.commit()
    return redirect('/cart')


@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if current_user.is_moder:
            product = db_sess.query(Product).filter(Product.id == product_id).first()
            cart = db_sess.query(Cart).filter(Cart.id == product_id).first()
            db_sess.delete(cart)
            db_sess.delete(product)
            db_sess.commit()
    return redirect('/')


@app.route('/clean', methods=['GET', 'POST'])
@login_required
def clean():
    db_sess = db_session.create_session()
    products = db_sess.query(Cart).filter(Cart.customer == current_user.email).all()
    for i in products:
        db_sess.delete(i)
    db_sess.commit()
    return redirect('/cart')


@app.route('/cart_fill/<int:product_id>', methods=['GET', 'POST'])
# @login_required
def cart_fill(product_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        product = db_sess.query(Product).get(product_id)
        user_cart = Cart()
        user_cart.product = product
        user_cart.customer = current_user.email
        db_sess.merge(user_cart)
        db_sess.commit()
        return redirect('/')
    else:
        return redirect('/login')


@app.route('/cart_fill_dealer/<int:product_id>', methods=['GET', 'POST'])
@login_required
def cart_fill_from_dealer(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    user_cart = Cart()
    user_cart.product = product
    user_cart.customer = current_user.email
    db_sess.merge(user_cart)
    db_sess.commit()
    return redirect(f'/user/{product.manufacturer_id}')


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    db_sess = db_session.create_session()
    products = db_sess.query(Cart)
    lst = []
    for i in products:
        if i:
            lst.append(i)
    return render_template('cart.html', title='Корзина', products=lst)


@app.route('/grid_sort_price')
def grid_sort_price():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index2.html', title='Товары', products=lst)


@app.route('/grid_sort_date')
def grid_sort_date():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.modified_date)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index2.html', title='Товары', products=lst)


@app.route('/grid_sort_price_min')
def grid_sort_price_min():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price.desc())
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index2.html', title='Товары', products=lst)
@app.route('/dealer_grid_sort_date')
@login_required
def dealer_grid_sort_date():
    db_sess = db_session.create_session()
    if current_user.is_moder:
        profiles = db_sess.query(User).order_by(Product.modified_date)
        lst = []
        for i in profiles:
            lst.append(i)
        return render_template('profiles.html', title='Profiles', profiles=lst)
    return redirect('/')


@app.route('/buy/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy(product_id):
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart).filter(Cart.customer == current_user.email).all()
    for i in cart:
        product = db_sess.query(Product).get(i.product_id)
        product.numb -= 1
    db_sess.delete(db_sess.query(Cart).filter(Cart.id == product_id).first())
    db_sess.commit()
    return redirect(
        'https://www.google.ru/maps/place/%D0%A8%D0%BA%D0%BE%D0%BB%D0%B0-%D0%98%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B0%D1%82/@55.5074358,47.4964615,82m/data=!3m1!1e3!4m15!1m8!3m7!1s0x415b9e232abc03d9:0x691cb4c9949a811b!2z0L_RgNC-0YHQvy4g0JvQtdC90LjQvdCwLCDQmtCw0L3QsNGILCDQp9GD0LLQsNGI0YHQutCw0Y8g0KDQtdGB0L8u!3b1!8m2!3d55.512611!4d47.5088236!16s%2Fg%2F1ymvmz7fn!3m5!1s0x415b9e20feded26f:0x783287a7a5126d20!8m2!3d55.5075859!4d47.4967289!16s%2Fg%2F1yfj9v31c')

@app.route('/about/<int:product_id>')
def about(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == product_id).first()
    return render_template('goods_page.html', products=product)
if __name__ == '__main__':
    db_session.global_init("db/store.db")
    app.run(port=8080, host='127.0.0.1')
