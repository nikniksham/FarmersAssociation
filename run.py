import datetime
import os
from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import abort, Api
from requests import put, delete
from werkzeug.utils import redirect
from data import db_session
from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, AdminListRecourse, UserResourceAdmin
from data.admin import Admin
from data.auditlog import AuditLog
from data.content import Content
from data.feedback import Feedback
from data.newsblock import Newsblock
from data.newspage import Newspage
from data.partner import Partner
from data.smartpage import Smartpage
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
api = Api(app)
api.add_resource(CreateAdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(AdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(UserResourceAdmin, "/api/admin/<string:email>/<string:password>/<int:user_id>")
api.add_resource(AdminListRecourse, "/api/admin/<string:email>/<string:password>")
login_manager = LoginManager()
db_session.global_init("db/FarmersAssociation.sqlite")


def main(port=8000):
    app.run(port=port)


@app.route("/")
def website_main():
    return render_template('pattern.html', title='Главная страница', style=url_for('static', filename='css/style.css'))


@app.route("/next")
def test_page():
    return render_template('test_page.html', title='Наследник от главной страницы',
                           style=url_for('static', filename='css/style.css'))


if __name__ == '__main__':
    main()
    create_new_db = False
    if create_new_db:
        db_session.global_init("db/FarmersAssociation.sqlite")
        session = db_session.create_session()
        admin = Admin()
        session.add(admin)
        session.add(AuditLog())
        session.add(Feedback())
        session.commit()
        session = db_session.create_session()
        session.add(Newsblock())
        session.add(Partner())
        session.add(Smartpage())
        session.commit()
        session = db_session.create_session()
        session.add(Content())
        session.add(Newspage())
        session.commit()
        print('Успех!')
