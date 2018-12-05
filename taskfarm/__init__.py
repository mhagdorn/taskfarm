from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

if __name__ != '__main__':
    # get gunicorn logger when the app is not run stand alone
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


from taskfarm import routes, models
