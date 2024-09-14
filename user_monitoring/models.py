
from datetime import datetime
from user_monitoring.db import db
# Created two models one for Users and one for UserEvent
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class UserEvent(db.Model):
    __tablename__ = 'user_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # I would change the column name to event_timestamp
    # as the integer isn't really a good data type for tracking user actions
    # in different timezones and we don't know when we started tracking the time of events
    #event_timestamp = db.Column(db.DateTime, nullable=False)
    event_time = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<UserEvent {self.id}>'