from flask_restful import reqparse

parser_auditlog = reqparse.RequestParser()
parser_auditlog.add_argument('admin_email', type=str)
parser_auditlog.add_argument('action', type=str)
parser_auditlog.add_argument('id', type=int)
