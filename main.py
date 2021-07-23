import datetime
import os
from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import abort, Api
from requests import put, delete
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
login_manager = LoginManager()


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
    main(port=8000)
