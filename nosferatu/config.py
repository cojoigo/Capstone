from datetime import timedelta

APP_NAME = 'Nosferatu'
DEBUG = False
CSRF_ENABLED = True
REMEMBER_COOKIE_DURATION = timedelta(days=3)
TESTING = False

CELERY_BROKER_URL = 'redis://localhost:6379',
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERYBEAT_SCHEDULE = {
    'add-every-10-seconds': {
        'task': 'nosferatu.tasks.rules_poll',
        'schedule': timedelta(seconds=10),
    },
}
# CELERYBEAT_SCHEDULE = 'nosferatu.sqlalchemy_scheduler:DatabaseScheduler'

# Flask-User Config
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
