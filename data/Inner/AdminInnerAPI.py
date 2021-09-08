import datetime
from data.user import User
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.Inner.main_file import raise_error, check_admin_status, check_admin

"""
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   Не трогай этот файл
   ok
"""


def check_password(password):
    errors = {0: 'Пароль должен быть в длину 8 или более символов', 1: 'Пароль должен содержать хотя бы 1 букву',
              2: 'Пароль должен содержать хотя бы 1 цифру'}
    if not len(password) >= 8:
        return raise_error(errors[0])
    if password.isdigit():
        return raise_error(errors[1])
    if password.isalpha():
        return raise_error(errors[2])
    return True


def find_by_id(id, session, status=0):
    user = session.query(User).get(id)
    if not user:
        return raise_error(f"Пользователь не найден", session), 1
    if user.status >= status or status < 1:
        return raise_error("У вас недостаточно прав для этого", session), 1
    return user, session


def edit_admin(args):
    count, f = 0, False
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error("Отсутствуют важные параметры")
    admin, session = check_admin(args['admin_email'])
    if args["action"] == "get":
        session.close()
        return admin.to_dict(only=('id', 'name', 'surname', 'status', 'email', 'created_date'))
    elif args["action"] == "get_list":
        admins = session.query(User).all()
        session.close()
        return [item.to_dict(only=('id', 'surname', 'name', 'status', 'email', 'created_date')) for item in admins]
    elif args["action"] == "delete":
        pass
    elif args["action"] == "put":
        admin_dict = admin.to_dict(only=('name', 'surname', 'email'))
        keys = list(filter(lambda key: args[key] is not None and key in admin_dict and args[key] != admin_dict[key], list(args.keys())))
        for key in keys:
            count += 1
            if key == 'email':
                if session.query(User).filter(User.email == args["email"]).first():
                    return raise_error("Этот email уже занят", session)
                admin.email = args['email']
            if key == 'name':
                admin.name = args["name"]
            if key == 'surname':
                admin.surname = args["surname"]
        if args["change_password"]:
            if not admin.check_password(args["check_admin_password"]):
                return raise_error("Пароль не совпадает с текущим паролем", session)
            check_password(args['new_admin_password'])
            admin.set_password(args['new_admin_password'])
            f, count = True, count + 1
        if count == 0:
            return raise_error("Пустой запрос", session)
        admin_dict_2 = admin.to_dict(only=('name', 'surname', 'email'))
        list_chang = [f'изменяет {key} с {admin_dict[key]} на {admin_dict_2[key]}' for key in keys]
        if f:
            list_chang.append("изменяет пароль")
        session.commit()
        add_auditlog("Изменение", f"Пользователь {admin.name} {admin.surname} изменяет сам себя: {', '.join(list_chang)}", admin,
                     datetime.datetime.now())
        session.close()
        return {"success": f"Пользователь {admin.name} {admin.surname} успешно изменён"}
    return raise_error("Неизвестный запрос", session)


def edit_admin_admin(user_id, args):
    count, f = 0, False
    if not all(args[key] is not None for key in ['admin_email', 'action']):  # При изменении себя/админов запрашивать пароль!!!!!!!!!!!
        return raise_error("Отсутствуют важные параметры")
    admin, session = check_admin_status(args['admin_email'], 1)
    user, session = find_by_id(user_id, session, admin.status)
    if type(user) == dict:
        return user
    if args["action"] == "get":
        session.close()
        return user.to_dict(only=('id', 'surname', 'name', 'status', 'email', 'created_date'))
    elif args["action"] == "delete":
        session.delete(user)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет админа {user.name} {user.surname}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Пользователь {user.name} {user.surname} успешно удалён"}
    elif args["action"] == "put":
        user_dict = user.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        keys = list(filter(lambda key: args[key] is not None and key in user_dict and args[key] != user_dict[key], list(args.keys())))
        for key in list(args.keys()):
            if args[key] is not None and (key == "password" or key in user_dict and args[key] != user_dict[key]):
                count += 1
                if key == 'email':
                    if session.query(User).filter(User.id == args["email"]).first():
                        return raise_error("Этот email уже занят", session)
                    user.email = args['email']
                if key == 'name':
                    user.name = args["name"]
                if key == 'surname':
                    user.surname = args["surname"]
                if key == 'status':
                    if admin.status < args['status']:
                        return raise_error("У вас недостаточно прав для этого", session)
                    user.status = args["status"]
        if "change_password" in args:
            if not admin.check_password(args["check_admin_password"]):
                return raise_error("Пароль не совпадает с текущим паролем", session)
            check_password(args['new_admin_password'])
            user.set_password(args['new_admin_password'])
            f, count = True, count + 1
        if count == 0:
            return raise_error("Пустой запрос", session)
        user_dict_2 = user.to_dict(only=('id', 'name', 'surname', 'status', 'email'))
        list_chang = [f'изменяет {key} с {user_dict[key]} на {user_dict_2[key]}' for key in keys]
        if f:
            list_chang.append("изменяет пароль")
        session.commit()
        add_auditlog("Изменение",
                     f"Админ {admin.name} {admin.surname} изменяет пользователя {user.name} {user.surname}: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Пользователь {user.name} {user.surname} успешно изменён"}
    return raise_error("Неизвестный запрос", session)


def create_admin(args):
    if not all(args[key] is not None for key in ['surname', 'name', 'email', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания пользователя')
    admin, session = check_admin_status(args['admin_email'])
    if session.query(User).filter(User.email == args['email']).first():
        return raise_error("Этот email уже занят", session)
    check_password(args["new_admin_password"])
    new_admin = User()
    new_admin.name = args["name"]
    new_admin.surname = args["surname"]
    new_admin.email = args['email']
    new_admin.set_password(args["new_admin_password"])
    if args['status'] is not None:
        if admin.status > args['status']:
            new_admin.status = args['status']
        else:
            return raise_error("Слишком высокий статус нового админа", session)
    else:
        new_admin.status = 0
    new_admin.created_date = datetime.datetime.now()
    session.add(new_admin)
    session.commit()
    add_auditlog("Создание",
                 f"Админ {admin.name} {admin.surname} создаёт админа {new_admin.name} {new_admin.surname}: {new_admin.to_dict(only=('id', 'name', 'surname', 'status', 'email'))}",
                 admin, datetime.datetime.now())
    session.close()
    return {'success': f'Пользователь {new_admin.name} {new_admin.surname} создан'}
