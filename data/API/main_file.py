from flask_restful import abort
from data.user import User
from data import db_session


def raise_error(error, session=None):
    if session:
        session.close()
    abort(400, message=error)


def check_admin_status(email, password, need_status=1):
    admin, session = check_admin(email, password)
    if admin.status < need_status:
        raise_error("У вас недостаточно прав для этого", session)
    return admin, session


def check_admin(email, password):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise_error(f"Админ {email} не найден", session)
    if not user.check_password(password):
        raise_error("Неправильный пароль", session)
    return user, session