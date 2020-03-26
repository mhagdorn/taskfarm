from .application import app, db
from .routes import *
from .models import *
import logging


if __name__ != '__main__':
    # get gunicorn logger when the app is not run stand alone
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)



