import datetime
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.address import Address
from data import db_session
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    address = session.query(Address).get(id)
    if not address:
        raise_error(f"Адрес не найден", session)
    return address, session


def edit_address(address_id, args):
    count = 0
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args["admin_email"], 1)
    address, session = find_by_id(address_id, session)
    if args['action'] == "get":
        session.close()
        return address.to_dict(only=('id', 'name', 'place'))
    elif args['action'] == 'put':
        address_dict = address.to_dict(only=('place',))
        keys = list(filter(lambda key: args[key] is not None and key in address_dict and args[key] != address_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'place':
                address.place = args["place"]
            if key == 'coord':
                address.coord = args["coord"]
        if count == 0:
            return raise_error("Пустой запрос", session)
        address_dict_2 = address.to_dict(only=('place',))
        list_chang = [f'изменяет {key} с {address_dict[key]} на {address_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"Админ {admin.name} {admin.surname} изменяет {address.name} адрес: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Адрес {address.name} успешно изменён"}


def get_address_list():
    session = db_session.create_session()
    addresss = session.query(Address).all()
    session.close()
    return [item.to_dict(only=('id', 'name', 'place')) for item in addresss]
