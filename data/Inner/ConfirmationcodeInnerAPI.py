import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from data import db_session
from data.confirmationcode import ConfirmationCode
import random
import datetime
import re
import smtplib
from data.bot import Bot

сложна