from flask_restful import reqparse

parser_feedback = reqparse.RequestParser()
parser_feedback.add_argument('fullname', type=str)
parser_feedback.add_argument('email', type=str)
parser_feedback.add_argument('heading', type=str)
parser_feedback.add_argument('image', type=str)
parser_feedback.add_argument('text', type=str)
