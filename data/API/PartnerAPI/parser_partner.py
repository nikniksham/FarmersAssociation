from flask_restful import reqparse

parser_partner = reqparse.RequestParser()
parser_partner.add_argument('id', type=int)
parser_partner.add_argument('name', type=str)
parser_partner.add_argument('image', type=str)
parser_partner.add_argument('text', type=str)
parser_partner.add_argument('link', type=str)
