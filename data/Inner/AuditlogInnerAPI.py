from data import db_session
from data.auditlog import AuditLog
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    auditlog = session.query(AuditLog).get(id)
    if not auditlog:
        return raise_error(f"Запись в журнале не найдена", session), 1
    return auditlog, session


def edit_auditlog(args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args["admin_email"])
    if args['action'] == "get":
        auditlog, session = find_by_id(args["id"], session)
        if type(auditlog) == dict:
            session.close()
            return auditlog
        session.close()
        return auditlog.to_dict(only=('id', 'event', 'info', 'user', 'created_date'))
    elif args['action'] == 'getlist':
        auditlogs = session.query(AuditLog).order_by(AuditLog.created_date).all()[::-1]
        session.close()
        return [item.to_dict(only=('id', 'event', 'info', 'user', 'created_date')) for item in auditlogs]


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
