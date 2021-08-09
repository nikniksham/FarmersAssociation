import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.user import User
from data.API.AdminAPI.parser_admin import parser_admin
from data.API.AuditlogAPI.AuditlogResource import add_auditlog


def raise_error(error):
    abort(400, message=error)


def check_password(password):
    errors = {0: 'Пароль должен быть в длину 8 или более символов', 1: 'Пароль должен содержать хотя бы 1 букву',
              2: 'Пароль должен содержать хотя бы 1 цифру'}
    if not len(password) >= 8:
        raise_error([0])
    if password.isdigit():
        raise_error(errors[1])
    if password.isalpha():
        raise_error(errors[2])
    return True


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


def find_by_id(id, session, status=0):
    user = session.query(User).get(id)
    if not user:
        raise_error(f"Пользователь не найден")
    if user.status >= status or status < 1:
        raise_error("У вас недостаточно прав для этого")
    return user, session


class AdminResource(Resource):
    def get(self, email, password):
        admin, session = check_admin(email, password)
        return jsonify(admin.to_dict(only=('id', 'name', 'surname', 'status', 'email')))

    def delete(self, email, password):
        admin, session = check_admin(email, password)
        name, surname = admin.name, admin.surname
        session.delete(admin)
        session.commit()
        add_auditlog("Удаление", f"Админ {name} {surname} удаляет свой аккаунт", admin, datetime.datetime.now())
        return jsonify({"success": f"Пользователь {name} {surname} успешно удалён"})

    def put(self, email, password):
        admin, session = check_admin(email, password)
        args, count = parser_admin.parse_args(), 0
        admin_dict = admin.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        keys = list(filter(lambda key: args[key] is not None and args[key] != admin_dict[key], list(args.keys())))
        for key in list(args.keys()):
            if args[key] is not None and args[key] != admin_dict[key]:
                count += 1
                if key == 'id':
                    if session.query(User).filter(User.id == args["id"]).first():
                        raise_error("Этот id уже занят")
                    admin.id = args['id']
                if key == 'email':
                    if session.query(User).filter(User.id == args["email"]).first():
                        raise_error("Этот email уже занят")
                    admin.email = args['email']
                if key == 'name':
                    admin.name = args["name"]
                if key == 'surname':
                    admin.surname = args["surname"]
                """if key == 'password':
                    check_password(args[key])
                    admin.set_password(password)"""
        if count == 0:
            return raise_error("Пустой запрос")
        admin_dict_2 = admin.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        list_chang = [f'изменяет {key} с {admin_dict[key]} на {admin_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Пользователь {admin.name} {admin.surname} изменяет сам себя: {', '.join(list_chang)}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Пользователь {admin.name} {admin.surname} успешно изменён"})


class AdminListRecourse(Resource):
    def get(self, email, password):
        admin, session = check_admin_status(email, password)
        admins = session.query(User).all()
        return jsonify([item.to_dict(only=('id', 'surname', 'name', 'status', 'email', 'created_date')) for item in admins])


class UserResourceAdmin(Resource):
    def get(self, email, password, user_id):
        admin, session = check_admin_status(email, password)
        user, session = find_by_id(user_id, session, admin.status)
        return jsonify(user.to_dict(only=('id', 'surname', 'name', 'status', 'email', 'created_date')))

    def delete(self, email, password, user_id):
        admin, session = check_admin_status(email, password, 2)
        user, session = find_by_id(user_id, session, admin.status)
        name, surname = user.name, user.surname
        session.delete(user)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет админа {name} {surname}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Пользователь {name} {surname} успешно удалён"})

    def put(self, email, password, user_id):
        admin, session = check_admin_status(email, password, 2)
        user, session = find_by_id(user_id, session, admin.status)
        args, count = parser_admin.parse_args(), 0
        user_dict = user.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        keys = list(filter(lambda key: args[key] is not None and args[key] != user_dict[key], list(args.keys())))
        for key in list(args.keys()):
            if args[key] is not None and args[key] != user_dict[key]:
                count += 1
                if key == 'email':
                    if session.query(User).filter(User.id == args["email"]).first():
                        raise_error("Этот email уже занят")
                    user.email = args['email']
                if key == 'name':
                    user.name = args["name"]
                if key == 'surname':
                    user.surname = args["surname"]
                if key == 'status':
                    if admin.status < args['status']:
                        raise_error("У вас недостаточно прав для этого")
                    user.status = args["status"]
        if count == 0:
            return raise_error("Пустой запрос")
        user_dict_2 = user.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        list_chang = [f'изменяет {key} с {user_dict[key]} на {user_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"Админ {admin.name} {admin.surname} изменяет пользователя {user.name} {user.surname}: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        return jsonify({"success": f"Пользователь {user.name} {user.surname} успешно изменён"})


class CreateAdminResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_admin.parse_args()
        if not all(args[key] is not None for key in ['surname', 'name', 'email', 'password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания пользователя')
        if session.query(User).filter(User.email == args['email']).first():
            raise_error("Этот email уже занят")
        check_password(args["password"])
        new_admin = User()
        new_admin.name = args["name"]
        new_admin.surname = args["surname"]
        new_admin.email = args['email']
        new_admin.set_password(args['password'])
        if args["id"] is not None:
            if session.query(User).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_admin.id = args["id"]
        if args['status'] is not None:
            if admin.status > args['status']:
                new_admin.status = args['status']
            else:
                raise_error("Слишком высокий статус нового админа")
        else:
            new_admin.status = 0
        new_admin.created_date = datetime.datetime.now()
        session.add(new_admin)
        session.commit()
        add_auditlog("Создание",
                     f"Админ {admin.name} {admin.surname} создаёт админа {new_admin.name} {new_admin.surname}: {new_admin.to_dict(only=('id', 'name', 'surname', 'status', 'email'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Пользователь {new_admin.name} {new_admin.surname} создан'})
