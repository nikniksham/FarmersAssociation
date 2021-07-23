import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from db_session import SqlAlchemyBase
from sqlalchemy import orm
from datetime import datetime


class NewsBlocks(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'newsblock'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    heading = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("admin.id"))
    author = orm.relation('Admin')

    def formatted_date(self):
        d = self.created_date
        return f"{str(d.year).rjust(2, '0')}.{str(d.month).rjust(2, '0')}.{d.day} {str(d.hour).rjust(2, '0')}:{str(d.minute).rjust(2, '0')}"
