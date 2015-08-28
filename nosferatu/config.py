import os
from datetime import timedelta


class FlaskUserConfig(object):
    USER_APP_NAME = 'Nosferatu'
    # USER_AFTER_LOGIN_ENDPOINT = '/'
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ENABLE_EMAIL = True
    USER_ENABLE_FORGOT_PASSWORD = False
    USER_ENABLE_LOGIN_WITHOUT_CONFIRM = True
    USER_ENABLE_CHANGE_USERNAME = False
    USER_ENABLE_USERNAME = False
    USER_SEND_PASSWORD_CHANGED_EMAIL = False
    USER_SEND_REGISTERED_EMAIL = False
    USER_SEND_USERNAME_CHANGED_EMAIL = False


class Config(FlaskUserConfig):
    APP_NAME = 'Nosferatu'
    DEBUG = False
    CSRF_ENABLED = True
    REMEMBER_COOKIE_DURATION = timedelta(days=3)
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
