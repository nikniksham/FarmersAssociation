import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from data import db_session
from data.confirmationcode import ConfirmationCode
import random
import datetime
import re
import smtplib
from data.bot import Bot

# x17dfWqpc94 farmersassociationmoscowregion
symbols = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890"
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


class CodeForConfirmation:
    def __init__(self):
        self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

    def create_code(self, email):
        session = db_session.create_session()
        old_code = session.query(ConfirmationCode).filter(ConfirmationCode.email == email).first()
        if old_code:
            session.delete(old_code)
        new_code = ConfirmationCode()
        code = "".join([random.choice(symbols) for i in range(6)])
        if self.send_message(email, code):
            new_code.set_code(code)
            new_code.email = email
            new_code.created_date = datetime.datetime.now()
            session.add(new_code)
            session.commit()
            return 'Код успешно создан'
        return "Проверьте правильность написания почты"

    def send_message(self, email, code):
        session = db_session.create_session()
        bot = session.query(Bot).get(1)
        self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        msg = MIMEMultipart()  # Создаем сообщение
        msg['From'] = bot.email  # Адресат
        msg['To'] = email  # Получатель
        msg['Subject'] = 'Код подтверждения'  # Тема сообщения
        html_code = f"""
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        </head>
        <body style="display:flex;justify-content:center;width:100%;">
            <div style="max-width:320px;background-color:#f4f4f4;width:100%;border-radius:15px;overflow:hidden;">
                <div style="height:55px;width:100%;padding-bottom:3px;background:#1e2f37;">
                    <img style="height:47px;padding-left:5%;padding-top:5px;" src="https://media.discordapp.net/attachments/547110396931211274/870716165574520913/logo-sm.png?width=1440&height=466" alt="logo">
                </div>
                <h1 style="text-align:center;">Код подтверждения.</h1>
                <p style="font-size:21px;padding:10px 5%;">Ваш код подтверждения, для написания отзыва на сайте Ассоциации Фермеров Московской Области: <b>{code}</b>, никому не сообщайте его</p>
                <div style="width:100%;padding-top:3px;background:#1e2f37;">
                    <p style="font-size:14px;padding:10px 5%;padding-bottom:20px;color:#eca137;margin:0;text-align:center;">Ассоциация фермеров Московской области</p>
                </div>
            </div>
        </body>
        </html>"""
        msg.attach(MIMEText(html_code, 'html', 'utf-8'))
        if re.search(regex, email):
            self.smtpObj.starttls()
            self.smtpObj.login(bot.email, bot.password)
            self.smtpObj.send_message(msg)
            self.smtpObj.quit()
            return True
        return False

    def attach_file(self, msg, filepath):  # Функция по добавлению конкретного файла к сообщению
        filename = os.path.basename(filepath)  # Получаем только имя файла
        ctype, encoding = mimetypes.guess_type(filepath)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        if maintype == 'image':  # Если изображение
            with open(filepath, 'rb') as fp:
                file = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
        file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
        msg.attach(file)

    def clear_codes(self):
        session = db_session.create_session()
        d_codes = []
        for code in session.query(ConfirmationCode).all():
            if (datetime.datetime.now() - code.created_date).total_seconds() > 180:
                d_codes.append(code.email)
                session.delete(code)
        session.commit()
        return f'Удалены коды {d_codes}'
