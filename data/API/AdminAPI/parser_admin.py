from flask_restful import reqparse

parser_admin = reqparse.RequestParser()
parser_admin.add_argument('id', type=int)
parser_admin.add_argument('password', type=str)
parser_admin.add_argument('name', type=str)
parser_admin.add_argument('surname', type=str)
parser_admin.add_argument('email', type=str)
parser_admin.add_argument('status', type=int)
