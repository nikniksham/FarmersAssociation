from flask_restful import reqparse

parser_address = reqparse.RequestParser()
parser_address.add_argument('place', type=str)
parser_address.add_argument('admin_email', type=str)
parser_address.add_argument('action', type=str)
