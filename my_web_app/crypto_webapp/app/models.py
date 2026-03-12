from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)



from datetime import datetime


class Sentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin = db.Column(db.String(50), nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    from datetime import datetime
from . import db

class TweetSentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

    from flask_login import UserMixin


class Coin(db.Model):
    __tablename__ = 'coins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)       # e.g., "Bitcoin"
    coin_id = db.Column(db.String(20), unique=True, nullable=False)    # e.g., "BTC-USD"

