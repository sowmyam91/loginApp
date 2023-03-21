from flask_login import UserMixin
from __init__ import db
from typing import Dict, Optional

# users: Dict[str, "User"] = {}
class User(UserMixin, db.Model):
    user_id = db.Column(db.String, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=False)
    name = db.Column(db.String(1000))
    def __init__(self, user_id: str, email: str, name: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def get_id(self):
        return self.user_id

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return User.query.get(user_id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True
