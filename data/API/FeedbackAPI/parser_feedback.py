from flask_restful import reqparse

parser_feedback = reqparse.RequestParser()
parser_feedback.add_argument('fullname', type=str)
parser_feedback.add_argument('email', type=str)
parser_feedback.add_argument('heading', type=str)
parser_feedback.add_argument('image', type=str)
parser_feedback.add_argument('text', type=str)
parser_feedback.add_argument('code', type=str)
parser_feedback.add_argument('admin_email', type=str)
parser_feedback.add_argument('action', type=str)
parser_feedback.add_argument('feedback_id', type=int)
parser_feedback.add_argument('admin_password', type=str)
