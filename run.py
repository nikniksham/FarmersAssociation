import datetime
import os
import time

from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import abort, Api
from requests import put, delete
from werkzeug.utils import redirect
from data import db_session
from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, AdminListRecourse, UserResourceAdmin
from data.API.AuditlogAPI.AuditlogResource import AuditlogResource, AuditlogListRecourse
from data.API.ConfirmationCodeAPI.ConfirmationcodeResource import CodeForConfirmation
from data.API.ContentAPI.ContentResource import CreateContentResource, ContentResource, ContentListRecourse
from data.API.FeedbackAPI.FeedbackResource import FeedbackResource, FeedbackListRecourse, CreateFeedbackResource
from data.API.NewspageAPI.NewspageResource import NewspageResource, NewspageListRecourse, CreateNewspageResource, NewspageResourceUsual
from data.API.PartnerAPI.PartnerResource import PartnerResource, PartnerResourceUsual, PartnerListRecourse, CreatePartnerResource
from data.API.SmartpageAPI.SmartpageResource import CreateSmartpageResource, SmartpageResource, SmartpageListRecourse
from data.admin import Admin
from data.auditlog import AuditLog
from data.content import Content
from data.feedback import Feedback
from data.newspage import Newspage
from data.partner import Partner
from data.smartpage import Smartpage
from data.forms import NewspageForm
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
api = Api(app)
api.add_resource(CreateAdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(AdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(UserResourceAdmin, "/api/admin/<string:email>/<string:password>/<int:user_id>")
api.add_resource(AdminListRecourse, "/api/admin/list/<string:email>/<string:password>")
api.add_resource(CreateSmartpageResource, "/api/smartpage/<string:email>/<string:password>")
api.add_resource(SmartpageResource, "/api/smartpage/<string:email>/<string:password>/<int:smartpage_id>")
api.add_resource(SmartpageListRecourse, "/api/smartpage")
api.add_resource(CreateContentResource, "/api/content/<string:email>/<string:password>")
api.add_resource(ContentResource, "/api/content/<string:email>/<string:password>/<int:content_id>")
api.add_resource(ContentListRecourse, "/api/content")
api.add_resource(AuditlogResource, "/api/auditlog/<string:email>/<string:password>/<int:auditlog_id>")
api.add_resource(AuditlogListRecourse, "/api/auditlog/<string:email>/<string:password>")
api.add_resource(CreateNewspageResource, "/api/newspage/<string:email>/<string:password>")
api.add_resource(NewspageResource, "/api/newspage/<string:email>/<string:password>/<int:newspage_id>")
api.add_resource(NewspageResourceUsual, "/api/newspage/<int:newspage_id>")
api.add_resource(NewspageListRecourse, "/api/newspage")
api.add_resource(CreatePartnerResource, "/api/partner/<string:email>/<string:password>")
api.add_resource(PartnerResource, "/api/partner/<string:email>/<string:password>/<int:partner_id>")
api.add_resource(PartnerResourceUsual, "/api/partner/<int:partner_id>")
api.add_resource(PartnerListRecourse, "/api/partner")
api.add_resource(FeedbackResource, "/api/feedback/<string:email>/<string:password>/<int:feedback_id>")
api.add_resource(FeedbackListRecourse, "/api/feedback/<string:email>/<string:password>")
api.add_resource(CreateFeedbackResource, "/api/feedback/<string:code>")
login_manager = LoginManager()
db_session.global_init("db/FarmersAssociation.sqlite")
code_helper = CodeForConfirmation()


def main(port=8000):
    # print(code_helper.create_code("yuramorozov2711@gmail.com"))
    # print(code_helper.create_code("nikniksham@gmail.com"))
    # code_helper.clear_codes()
    """session = db_session.create_session()
    session.execute("alter table feedback add column 'heading' 'varchar'")"""
    app.run(port=port)


@app.route("/")
def website_main():
    return render_template('main.html', title='Главная страница', style=url_for('static', filename='css/style.css'))


@app.route("/next")
def test_page():
    return render_template('test_page.html', title='Наследник от главной страницы',
                           style=url_for('static', filename='css/style.css'))


@app.route("/admin")
def admin():
    form = NewspageForm()
    return render_template('admin-panel.html', title='админка',
                           style=url_for('static', filename='css/style.css'), form=form)


if __name__ == '__main__':
    print("http://127.0.0.1:8000/admin")
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
        session.add(Newspage())
        session.add(Partner())
        session.add(Smartpage())
        session.commit()
        session = db_session.create_session()
        session.add(Content())
        session.commit()
        print('Успех!')
