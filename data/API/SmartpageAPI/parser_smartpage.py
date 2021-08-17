from flask_restful import reqparse

parser_smartpage = reqparse.RequestParser()
parser_smartpage.add_argument('id', type=int)
parser_smartpage.add_argument('heading', type=str)
parser_smartpage.add_argument('image', type=str)
parser_smartpage.add_argument('admin_email', type=str)
parser_smartpage.add_argument('action', type=str)
parser_smartpage.add_argument('admin_password', type=str)
