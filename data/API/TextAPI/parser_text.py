from flask_restful import reqparse

parser_text = reqparse.RequestParser()
parser_text.add_argument('heading', type=str)
parser_text.add_argument('description', type=str)
parser_text.add_argument('admin_email', type=str)
parser_text.add_argument('action', type=str)
parser_text.add_argument('admin_password', type=str)
