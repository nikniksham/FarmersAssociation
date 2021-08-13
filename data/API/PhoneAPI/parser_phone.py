from flask_restful import reqparse

parser_phone = reqparse.RequestParser()
parser_phone.add_argument('number', type=str)
parser_phone.add_argument('admin_email', type=str)
parser_phone.add_argument('action', type=str)
