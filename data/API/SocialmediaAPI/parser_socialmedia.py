from flask_restful import reqparse

parser_socialmedia = reqparse.RequestParser()
parser_socialmedia.add_argument('icon_type', type=str)
parser_socialmedia.add_argument('link', type=str)
parser_socialmedia.add_argument('admin_email', type=str)
parser_socialmedia.add_argument('action', type=str)
