from flask_restful import reqparse

parser_email = reqparse.RequestParser()
parser_email.add_argument('email_address', type=str)
parser_email.add_argument('admin_email', type=str)
parser_email.add_argument('action', type=str)
parser_email.add_argument('admin_password', type=str)
