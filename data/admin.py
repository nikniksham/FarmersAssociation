import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Admin(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'admin'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)
    smartpage = orm.relation('Smartpage')
    newsblocks = orm.relation('Newsblock')
    partner = orm.relation('Partner')
    content = orm.relation('Content')
    newspage = orm.relation('Newspage')

    def __repr__(self):
        return f'<Admin> {self.id} Админ {self.id} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def formatted_date(self):
        d = self.created_date
        return f"{str(d.year).rjust(2, '0')}.{str(d.month).rjust(2, '0')}.{d.day} {str(d.hour).rjust(2, '0')}:{str(d.minute).rjust(2, '0')}"
