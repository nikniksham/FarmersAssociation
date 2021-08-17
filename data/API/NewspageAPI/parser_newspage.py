from flask_restful import reqparse

parser_newspage = reqparse.RequestParser()
parser_newspage.add_argument('id', type=int)
parser_newspage.add_argument('heading', type=str)
parser_newspage.add_argument('text', type=str)
parser_newspage.add_argument('link', type=str)
parser_newspage.add_argument('image', type=str)
parser_newspage.add_argument('tags', type=str)
parser_newspage.add_argument('admin_email', type=str)
parser_newspage.add_argument('action', type=str)
parser_newspage.add_argument('admin_password', type=str)
