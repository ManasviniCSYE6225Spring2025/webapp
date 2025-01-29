
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class HealthCheck(db.Model):
    __tablename__ = "health_check"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
