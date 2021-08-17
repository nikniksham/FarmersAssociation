from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.user import User
from data.auditlog import AuditLog
from data.API.AuditlogAPI.parser_auditlog import parser_auditlog


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
    content = session.query(AuditLog).get(id)
    if not content:
        raise_error(f"Запись в журнале не найдена")
    return content, session


class AuditlogResource(Resource):
    def put(self):
        args = parser_auditlog.parse_args()
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args["admin_email"], args["admin_password"])
        if args['action'] == "get":
            content, session = find_by_id(args["id"], session)
            return jsonify(content.to_dict(only=('id', 'event', 'info', 'user', 'created_date')))
        elif args['action'] == 'getlist':
            contents = session.query(AuditLog).order_by(AuditLog.created_date).all()[::-1]
            return jsonify([item.to_dict(only=('id', 'event', 'info', 'user', 'created_date')) for item in contents])


def add_auditlog(event, info, user, datetime):
    session = db_session.create_session()
    new_auditlog = AuditLog()
    new_auditlog.event = event
    new_auditlog.info = info
    if user:
        new_auditlog.user = user.id
    new_auditlog.datetime = datetime
    session.add(new_auditlog)
    session.commit()