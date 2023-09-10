import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'abcd'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'parking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'example@gmail.com'
    MAIL_PASSWORD = 'password'
    SESSION_COOKIE_SECURE = True
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    JSON_SORT_KEYS = False
