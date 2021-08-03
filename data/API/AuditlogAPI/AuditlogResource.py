from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.user import User
from data.auditlog import AuditLog


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
    def get(self, email, password, auditlog_id):
        admin, session = check_admin_status(email, password)
        content, session = find_by_id(auditlog_id, session)
        return jsonify(content.to_dict(only=('id', 'event', 'info', 'user', 'created_date')))


class AuditlogListRecourse(Resource):
    def get(self, email, password):
        admin, session = check_admin_status(email, password)
        contents = session.query(AuditLog).order_by(AuditLog.created_date).all()
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