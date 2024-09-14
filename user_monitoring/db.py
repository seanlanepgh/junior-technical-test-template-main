from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#From looking at the task I should see that a database would
# be needed to keep track of UserEvents for the /events 
# as for some alert code may require consecutive calls to the api

db = SQLAlchemy()

def setup_db(app):
    """
    Set up the database for the Flask application.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    setup_db(app)

    from user_monitoring.models import User, UserEvent

    return app
