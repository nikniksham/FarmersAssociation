from flask_restful import reqparse

parser_seo = reqparse.RequestParser()
parser_seo.add_argument('title', type=str)
parser_seo.add_argument('description', type=str)
parser_seo.add_argument('tags', type=str)
parser_seo.add_argument('admin_email', type=str)
parser_seo.add_argument('action', type=str)
