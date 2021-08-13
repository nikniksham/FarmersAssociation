import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.worker import Worker
from data.API.WorkerAPI.parser_worker import parser_worker
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
    worker = session.query(Worker).get(id)
    if not worker:
        raise_error(f"Сотрудник не найден")
    return worker, session


class WorkerResource(Resource):
    def put(self, worker_id):
        args, count = parser_worker.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args["admin_email"], password_manager.get_password(args["admin_email"]))
        worker, session = find_by_id(worker_id, session)
        if args['action'] == "get":
            return jsonify(worker.to_dict(only=('id', 'image', 'name', 'profession', 'phone', 'email', 'created_date')))
        elif args['action'] == 'delete':
            session.delete(worker)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет сотрудника: {worker.name}", admin, datetime.datetime.now())
            return jsonify({"success": f"Сотрудник {worker.name} успешно удален"})
        elif args['action'] == 'put':
            work_dict = worker.to_dict(only=('image', 'name', 'profession', 'phone', 'email'))
            keys = list(filter(lambda key: args[key] is not None and key in work_dict.keys() and args[key] != work_dict[key], list(args.keys())))
            name = worker.name
            for key in keys:
                count += 1
                if key == 'image':
                    worker.image = args['image']
                if key == "name":
                    worker.name = args["name"]
                if key == "profession":
                    worker.profession = args["profession"]
                if key == "phone":
                    worker.phone = args["phone"]
                if key == "email":
                    worker.email = args["email"]
            if count == 0:
                return raise_error("Пустой запрос")
            work_dict_2 = worker.to_dict(only=('image', 'name', 'profession', 'phone', 'email'))
            list_chang = [f'изменяет {key} с {work_dict[key]} на {work_dict_2[key]}' if key not in ["image"] else "изменяет изображения" for key in keys]
            session.commit()
            add_auditlog("Изменение",
                         f"{admin.name} {admin.surname} изменяет сотрудника {name}: {', '.join(list_chang)}", admin,
                         datetime.datetime.now())
            return jsonify({"success": f"Сотрудник {name} успешно изменен"})
        raise_error("Неизвестный метод")


class WorkerResourceUsual(Resource):
    def get(self, worker_id):
        session = db_session.create_session()
        worker, session = find_by_id(worker_id, session)
        return jsonify(worker.to_dict(only=('id', 'image', 'name', 'profession', 'phone', 'email', 'created_date')))


class WorkerListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        workers = session.query(Worker).all()
        return jsonify([item.to_dict(only=('id', 'image', 'name', 'profession', 'phone', 'email', 'created_date')) for item in workers])


class CreateWorkerResource(Resource):
    def post(self):
        args = parser_worker.parse_args()
        if not all(args[key] is not None for key in ['image', 'name', 'profession', 'phone', 'email', 'admin_email']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания партнёра')
        admin, session = check_admin_status(args["admin_email"], password_manager.get_password(args["admin_email"]))
        new_worker = Worker()
        new_worker.image = args["image"]
        new_worker.name = args["name"]
        new_worker.profession = args["profession"]
        new_worker.phone = args["phone"]
        new_worker.email = args["email"]
        new_worker.profession = args["profession"]
        new_worker.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Worker).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_worker.id = args["id"]
        session.add(new_worker)
        session.commit()
        params_dict = new_worker.to_dict(only=('id', 'image', 'name', 'profession', 'phone', 'email', 'created_date'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание", f"{admin.name} {admin.surname} создаёт сотрудника {new_worker.name}: {params_dict}",
                     admin, datetime.datetime.now())
        print(new_worker.id)
        return jsonify({'success': f'Сотрудник {new_worker.name} создан', 'id': new_worker.id})
