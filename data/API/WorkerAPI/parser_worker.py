from flask_restful import reqparse

parser_worker = reqparse.RequestParser()
parser_worker.add_argument('id', type=int)
parser_worker.add_argument('image', type=str)
parser_worker.add_argument('name', type=str)
parser_worker.add_argument('profession', type=str)
parser_worker.add_argument('phone', type=str)
parser_worker.add_argument('email', type=str)
parser_worker.add_argument('admin_email', type=str)
parser_worker.add_argument('action', type=str)
