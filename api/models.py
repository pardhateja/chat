from api import db
import datetime


# DB model for relation (id, public_id, name, phone, password)
# This relation stores the details of each user who has signup his account.
# public_id is a unique id made of uuid4 for maintaining unique values.
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(50),unique=True)
    name=db.Column(db.String(50))
    phone=db.Column(db.String(80),unique=True)
    password=db.Column(db.String(80))

# DB model for relation (id, message_text, time, message_state, user_id)
# This relation stores the details of each message.
# Here id is generated with 100+userid+10000+value_unique of user who is sending
class Messages(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    message_text=db.Column(db.String(150))
    time=db.Column(db.DateTime, default=datetime.datetime.utcnow)
    from_phone=db.Column(db.Integer)
    to_phone=db.Column(db.Integer)

# DB model for relation (id, phone, unique_id)
# This relation stores the details of each user with the present unique_id.
class User_Unique(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    phone=db.Column(db.String(80),unique=True)
    unique_id=db.Column(db.Integer)
