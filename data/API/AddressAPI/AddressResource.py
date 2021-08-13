import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.AddressAPI.parser_address import parser_address
from data.address import Address
from main import password_manager


def raise_error(error):
    abort(400, message=error)


def check_admin_status(email, password, need_status=1):
    admin, session = check_admin(email, password)
    if admin.status < need_status:
        raise_error("У вас недостаточно прав для этого")
    return admin, session


def check_admin(email, password):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise_error(f"Админ {email} не найден")
    if not user.check_password(password):
        raise_error("Неправильный пароль")
    return user, session


def find_by_id(id, session):
    address = session.query(Address).get(id)
    if not address:
        raise_error(f"Адрес не найден")
    return address, session


class AddressListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        addresss = session.query(Address).all()
        return jsonify([item.to_dict(only=('id', 'name', 'place')) for item in addresss])


class AdminResourceAddress(Resource):
    def get(self, email, password, address_id):
        admin, session = check_admin_status(email, password)
        address, session = find_by_id(address_id, session)
        return jsonify(address.to_dict(only=('id', 'name', 'place')))

    def put(self, email, password, address_id):
        admin, session = check_admin_status(email, password, 2)
        address, session = find_by_id(address_id, session)
        args, count = parser_address.parse_args(), 0
        address_dict = address.to_dict(only=('place'))
        keys = list(filter(lambda key: args[key] is not None and key in address_dict and args[key] != address_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'place':
                address.place = args["place"]
        if count == 0:
            return raise_error("Пустой запрос")
        address_dict_2 = address.to_dict(only=('place'))
        list_chang = [f'изменяет {key} с {address_dict[key]} на {address_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет {address.name} адрес: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        return jsonify({"success": f"Адрес {address.name} успешно изменён"})
