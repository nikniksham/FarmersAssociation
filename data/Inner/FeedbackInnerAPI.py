import datetime
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.feedback import Feedback
from data.confirmationcode import ConfirmationCode
from main import text_transform
from config import UPLOAD_FOLDER as path
from data.Inner.main_file import raise_error, check_admin_status


def check_code(session, email, code):
    ch_code = session.query(ConfirmationCode).filter(ConfirmationCode.email == email).first()
    if not ch_code:
        return raise_error("Срок действия кода истёк", session)
    if (datetime.datetime.now() - ch_code.created_date).total_seconds() > 180:
        return raise_error("Срок действия кода истёк", session)
    if not ch_code.check_code(code):
        return raise_error("Проверьте правильность написания кода", session)
    return ch_code


def find_by_id(id, session):
    feedback = session.query(Feedback).get(id)
    if not feedback:
        return raise_error(f"Отзыв не найден", session)
    return feedback, session


def edit_feedback(args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    if args['action'] == "get":
        feedback, session = find_by_id(args["feedback_id"], session)
        news_dict = feedback.to_dict(only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
        news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
        session.close()
        return news_dict
    elif args['action'] == "getlist":
        feedbacks, dict_list = session.query(Feedback).all()[::-1], []
        for feedback in feedbacks:
            news_dict = feedback.to_dict(
                only=('id', 'fullname', 'heading', 'email', 'image', 'text', 'created_date'))
            news_dict["text_render"] = text_transform(feedback.text, feedback.image.split("//"), path)
            dict_list.append(news_dict)
        session.close()
        return dict_list
    elif args['action'] == 'delete':
        feedback, session = find_by_id(args["feedback_id"], session)
        session.delete(feedback)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет отзыв {feedback.heading} от пользователя {feedback.fullname}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Отзыв {feedback.heading} от пользователя {feedback.fullname} успешно удален"}
    return raise_error("Неизвестный метод", session)


def feedback_edit_image(feedback_id, code, args):
    session = db_session.create_session()
    feedback, session = find_by_id(feedback_id, session)
    if not feedback.code:
        return raise_error("невозмоно менять повторно", session)
    if feedback.code != code:
        return raise_error("неизвестный код", session)
    feedback.code = None
    if args["image"]:
        feedback.image = args["image"]
    session.commit()
    session.close()
    return {"success": "картинки успешно изменены"}


def create_feedback(args):
    session = db_session.create_session()
    if not all(args[key] is not None for key in ['fullname', 'heading', 'email', 'text', 'code']):
        return raise_error('Пропущены некоторые аргументы, необходимые для оставления отзыва', session)
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
    return {'id': new_feedback.id, 'success': f'{new_feedback.fullname} оставил отзыв'}
