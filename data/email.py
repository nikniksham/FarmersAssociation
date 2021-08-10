import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Email(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'email'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
