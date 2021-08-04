import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
from datetime import datetime


class Feedback(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'feedback'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    heading = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fullname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

    def formatted_date(self):
        d = self.created_date
        return f"{str(d.year).rjust(2, '0')}.{str(d.month).rjust(2, '0')}.{d.day} {str(d.hour).rjust(2, '0')}:{str(d.minute).rjust(2, '0')}"
