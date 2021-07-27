from flask_restful import reqparse

put_parser_admin = reqparse.RequestParser()
put_parser_admin.add_argument('id', type=int)
put_parser_admin.add_argument('name', type=str)
put_parser_admin.add_argument('surname', type=str)
put_parser_admin.add_argument('email', type=str)
put_parser_admin.add_argument('password', type=str)
put_parser_admin.add_argument('status', type=int)
