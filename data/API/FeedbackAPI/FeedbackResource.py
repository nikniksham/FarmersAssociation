import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.feedback import Feedback
from data.confirmationcode import ConfirmationCode
from data.API.FeedbackAPI.parser_feedback import parser_feedback
from main import text_transform
from config import UPLOAD_FOLDER as path


def raise_error(error):
    abort(400, message=error)


def check_code(session, email, code):
    ch_code = session.query(ConfirmationCode).filter(ConfirmationCode.email == email).first()
    if not ch_code:
        raise_error("Срок действия кода истёк")
    if (datetime.datetime.now() - ch_code.created_date).total_seconds() > 180:
        raise_error("Срок действия кода истёк")
    if not ch_code.check_code(code):
        raise_error("Проверьте правильность написания кода")
    return ch_code


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
    feedback = session.query(Feedback).get(id)
    if not feedback:
        raise_error(f"Отзыв не найден")
    return feedback, session


class FeedbackResource(Resource):
    def get(self, email, password, feedback_id):
        admin, session = check_admin_status(email, password)
        feedback, session = find_by_id(feedback_id, session)
        news_dict = feedback.to_dict(only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
        news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
        return jsonify(news_dict)

    def delete(self, email, password, feedback_id):
        admin, session = check_admin_status(email, password)
        feedback, session = find_by_id(feedback_id, session)
        fullname = feedback.fullname
        session.delete(feedback)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет отзыв {fullname}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Отзыв {fullname} успешно удален"})


class FeedbackListRecourse(Resource):
    def get(self, email, password):
        admin, session = check_admin_status(email, password)
        feedbacks, dict_list = session.query(Feedback).all(), []
        for feedback in feedbacks:
            news_dict = feedback.to_dict(only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
            news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
            dict_list.append(news_dict)
        return jsonify(dict_list)


class CreateFeedbackResource(Resource):
    def post(self):
        session = db_session.create_session()
        args = parser_feedback.parse_args()
        if not all(args[key] is not None for key in ['fullname', 'heading', 'email', 'text', 'code']):
            raise_error('Пропущены некоторые аргументы, необходимые для оставления отзыва')
        ch_code = check_code(session, args["email"], args["code"])
        new_feedback = Feedback()
        new_feedback.fullname = args["fullname"]
        new_feedback.image = args["image"] if args["image"] else ""
        new_feedback.heading = args["heading"]
        new_feedback.email = args["email"]
        new_feedback.text = args["text"]
        new_feedback.created_date = datetime.datetime.now()
        session.add(new_feedback)
        session.delete(ch_code)
        session.commit()
        # f'кол-во картинок: ' + str(len(new_feedback.image.split('//')))
        params_dict = new_feedback.to_dict(only=('fullname', 'heading', 'email', 'text', 'created_date'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//")) if args["image"] else 0}'
        add_auditlog("Создание",
                     f"{args['fullname']} оставляет отзыв: {params_dict}", None, datetime.datetime.now())
        return jsonify({'success': f'{new_feedback.fullname} оставил отзыв'})
