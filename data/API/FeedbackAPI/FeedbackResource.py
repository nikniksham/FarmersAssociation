import datetime
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.feedback import Feedback
from data.confirmationcode import ConfirmationCode
from data.API.FeedbackAPI.parser_feedback import parser_feedback
from main import text_transform
from config import UPLOAD_FOLDER as path
from data.API.main_file import raise_error, check_admin_status


def check_code(session, email, code):
    ch_code = session.query(ConfirmationCode).filter(ConfirmationCode.email == email).first()
    if not ch_code:
        raise_error("Срок действия кода истёк", session)
    if (datetime.datetime.now() - ch_code.created_date).total_seconds() > 180:
        raise_error("Срок действия кода истёк", session)
    if not ch_code.check_code(code):
        raise_error("Проверьте правильность написания кода", session)
    return ch_code


def check_admin(email, password):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise_error(f"Админ {email} не найден", session)
    if not user.check_password(password):
        raise_error("Неправильный пароль", session)
    return user, session


def find_by_id(id, session):
    feedback = session.query(Feedback).get(id)
    if not feedback:
        raise_error(f"Отзыв не найден", session)
    return feedback, session


class FeedbackResource(Resource):
    def put(self):
        args = parser_feedback.parse_args()
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        if args['action'] == "get":
            feedback, session = find_by_id(args["feedback_id"], session)
            news_dict = feedback.to_dict(only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
            news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
            session.close()
            return jsonify(news_dict)
        elif args['action'] == "getlist":
            feedbacks, dict_list = session.query(Feedback).all()[::-1], []
            for feedback in feedbacks:
                news_dict = feedback.to_dict(
                    only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
                news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
                dict_list.append(news_dict)
            session.close()
            return jsonify(dict_list)
        elif args['action'] == 'delete':
            feedback, session = find_by_id(args["feedback_id"], session)
            session.delete(feedback)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет отзыв {feedback.heading} от пользователя {feedback.fullname}",
                         admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Отзыв {feedback.heading} от пользователя {feedback.fullname} успешно удален"})
        raise_error("Неизвестный метод", session)


class FeedbackTransportImage(Resource):
    def put(self, feedback_id, code):
        session = db_session.create_session()
        feedback, session = find_by_id(feedback_id, session)
        if not feedback.code:
            return raise_error("невозмоно менять повторно", session)
        if feedback.code != code:
            return raise_error("неизвестный код", session)
        feedback.code = None
        args = parser_feedback.parse_args()
        print(args)
        if args["image"]:
            feedback.image = args["image"]
        print(feedback.image)
        session.commit()
        session.close()
        return jsonify({"success": "картинки успешно изменены"})


class CreateFeedbackResource(Resource):
    def post(self):
        session = db_session.create_session()
        args = parser_feedback.parse_args()
        if not all(args[key] is not None for key in ['fullname', 'heading', 'email', 'text', 'code']):
            raise_error('Пропущены некоторые аргументы, необходимые для оставления отзыва', session)
        ch_code = check_code(session, args["email"], args["code"])
        new_feedback = Feedback()
        new_feedback.code = args["code"]
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
        session.close()
        return jsonify({'success': f'{new_feedback.fullname} оставил отзыв', 'id': new_feedback.id})
