from flask_restful import reqparse

parser_admin = reqparse.RequestParser()
parser_admin.add_argument('id', type=int)
parser_admin.add_argument('name', type=str)
parser_admin.add_argument('surname', type=str)
parser_admin.add_argument('email', type=str)
parser_admin.add_argument('status', type=int)
parser_admin.add_argument('admin_email', type=str)
parser_admin.add_argument('action', type=str)
parser_admin.add_argument('admin_password', type=str)
parser_admin.add_argument('check_admin_password', type=str)
parser_admin.add_argument('new_admin_password', type=str)
parser_admin.add_argument('change_password', type=bool)
