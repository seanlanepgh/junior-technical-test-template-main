
import logging
import os
from flask import Flask
from user_monitoring.db import db, setup_db
from user_monitoring.models import User, UserEvent
from werkzeug.security import generate_password_hash

def create_app() -> Flask:
    app = Flask("user_monitoring")
    setup_db(app)
    
     # Call db.create_all() to create the database tables
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    from user_monitoring.api import api as api_blueprint
    
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'UserEvent': UserEvent}

    app.register_blueprint(api_blueprint)
    return app


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)

# Created an admin user just for this example 
# There would be more than one user in a real life example 
def create_admin_user():
    """
    Create an admin user if the User table is empty.
    """
    admin_user = User(
        username=os.environ.get('ADMIN_USERNAME', 'admin'),
        email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'),
        password=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'password')),
    )
    if not User.query.first():
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully.')
    else:
        print('Admin user already exists.')

