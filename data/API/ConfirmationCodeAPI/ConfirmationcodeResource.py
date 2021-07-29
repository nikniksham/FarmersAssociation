import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.confirmationcode import ConfirmationCode
import random

symbols = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890"


def generate_code(len):
    code = "".join([random.choice(symbols) for i in range(len)])
    print(code)
    return code


def create_code(email):
    session = db_session.create_session()
    old_code = session.query(ConfirmationCode).filter(ConfirmationCode.email == email).first()
    if old_code:
        session.delete(old_code)
    new_code = ConfirmationCode()
    new_code.set_code(generate_code(6))
    new_code.email = email
    new_code.created_date = datetime.datetime.now()
    session.add(new_code)
    session.commit()
    return 'Код успешно создан'


def clear_codes():
    session = db_session.create_session()
    d_codes = []
    for code in session.query(ConfirmationCode).all():
        if (datetime.datetime.now() - code.created_date).total_seconds() > 180:
            d_codes.append(code.email)
            session.delete(code)
    session.commit()
    return f'Удалены коды {d_codes}'