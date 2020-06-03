"""
This module contains the models for yahtzee. It also makes use of SQLAlchemy
"Model" class and Marshmallow "SQLAlchemyAutoSchema" class inheretence.
"""

from datetime import datetime
from config import db, ma


class User(db.Model):
    """
    User model which defines the user attributes and SQLite3 db table/fields.
    """
    __tablename__ = "user"
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
        )

    def __repr__(self):
        return (
            f"User('{self.user_id}', '{self.username}', '{self.first_name}', "
            f"'{self.last_name}', '{self.email}')"
        )


class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    This user schema inherets from SQLAlchemyAutoSchema and uses the Meta
    class to find the SQLAlchemy model User and the db.session.
    """
    class Meta:
        model = User
        sqla_session = db.session


class Game(db.Model):
    """
    Game model which defines the game attributes and db table/fields.
    """
    __tablename__ = "game"
    game_id = db.Column(db.Integer, nullable=False, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Game('{self.game_id}', '{self.timestamp}'"


class GameSchema(ma.SQLAlchemyAutoSchema):
    """
    This game schema inherets from SQLAlchemyAutoSchema and uses the Meta
    class to find the SQLAlchemy model Game and the db.session.
    """
    class Meta:
        model = Game
        sqla_session = db.session
