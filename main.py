from flask import Flask, url_for, request, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import db_session
from data.products import Product
from data.users import User
from forms.login_forms import LoginForm
from forms.product import ProductForm
from forms.user import RegisterForm, UserEditForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        products = db_sess.query(Product)
        return render_template('index.html', title='Товары', products=products)
    else:
        return redirect('/login')


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
            is_admin=False
        )
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
            if form.password.data:
                user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('create_profile.html', edit=True, title='Редактирование', form=form)


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template('user.html', title='Страница', user=user)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = ProductForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        product = Product()
        product.title = form.title.data
        product.price = form.price.data
        product.about = form.about.data

        # current_user.news.append(news)
        # db_sess.merge(current_user)

        product.manufacturer = current_user
        db_sess.merge(product)

        db_sess.commit()
        return redirect('/')
    return render_template('create.html', title='Добавление продукта',
                           form=form)


@app.route('/product_delete/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_delete(product_id):
    db_sess = db_session.create_session()
    if current_user.is_admin:
        product = db_sess.query(Product).filter(Product.id == product_id,
                                                Product.manufacturer == current_user).first()
    else:
        product = None
    if product:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    db_session.global_init("db/store.db")
    app.run(port=8080, host='127.0.0.1')
