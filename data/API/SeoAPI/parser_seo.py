from flask_restful import reqparse

parser_address = reqparse.RequestParser()
parser_address.add_argument('title', type=str)
parser_address.add_argument('description', type=str)
parser_address.add_argument('tags', type=str)
parser_address.add_argument('admin_email', type=str)
parser_address.add_argument('action', type=str)
