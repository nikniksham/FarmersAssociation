from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.auditlog import AuditLog
from data.API.AuditlogAPI.parser_auditlog import parser_auditlog
from data.API.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    content = session.query(AuditLog).get(id)
    if not content:
        raise_error(f"Запись в журнале не найдена", session)
    return content, session


class AuditlogResource(Resource):
    def put(self):
        args = parser_auditlog.parse_args()
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args["admin_email"], args["admin_password"])
        if args['action'] == "get":
            content, session = find_by_id(args["id"], session)
            session.close()
            return jsonify(content.to_dict(only=('id', 'event', 'info', 'user', 'created_date')))
        elif args['action'] == 'getlist':
            contents = session.query(AuditLog).order_by(AuditLog.created_date).all()[::-1]
            session.close()
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
    session.close()
