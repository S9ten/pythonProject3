import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # название товара
    manufacturer_id = sqlalchemy.Column(sqlalchemy.String,
                                        sqlalchemy.ForeignKey("users.dealer_id"))
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    numb = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="products")
    manufacturer = orm.relationship('User')
    cart = orm.relationship('Cart', back_populates='product')
