from flask_restful import reqparse

parser_partner = reqparse.RequestParser()
parser_partner.add_argument('logo', type=str)
parser_partner.add_argument('image', type=str)
parser_partner.add_argument('name', type=str)
parser_partner.add_argument('info', type=str)
parser_partner.add_argument('preferences', type=str)
parser_partner.add_argument('address', type=str)
parser_partner.add_argument('link', type=str)
parser_partner.add_argument('socialmedia', type=str)
parser_partner.add_argument('admin_email', type=str)
parser_partner.add_argument('action', type=str)
parser_partner.add_argument('admin_password', type=str)
