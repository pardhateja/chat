from api import app, db
from flask import request, jsonify,make_response
from api.models import Messages,User,User_Unique
from __main__ import app
import json
import uuid,jwt,datetime
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
import re



#This method is for deleting all the tables which were created as of now.
#Uncomment if needed.
# @app.route('/test', methods=['GET'])
# def test():
#     Messages.query.delete()
#     User.query.delete()
#     db.session.commit()
#
#     return 'it works!'

def isValid(s):

    # 1) Begins with 0 or 91
    # 2) Then contains 7 or 8 or 9.
    # 3) Then contains 9 digits
    Pattern = re.compile("(0|91)?[7-9][0-9]{9}")
    return Pattern.match(s)


#Route for signup of the user
@app.route('/signup', methods=['POST'])
def signup():
    data=request.get_json()
    phone=data['phone']
    valid = isValid(phone)
    if(not valid):
        return jsonify({"status": 202, "message": "Phone number is invalid"})

    user_exists = User.query.filter_by(phone=phone).first()

    if(user_exists):
        return jsonify({"status": 202, "message": "There is alredy a user with the same phone number please login."})

    password=data['password']

    if(len(password)<=6):
        return jsonify({"status": 202, "message": "The password is too short."})

    hashed_password=generate_password_hash(password, method='sha256')
    new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,phone=phone)
    db.session.add(new_user)
    db.session.commit()
    user_unique=User_Unique(phone=phone,unique_id=1)
    db.session.add(user_unique)
    db.session.commit()


    return jsonify({"status": 201, "message": "The user has been created."})



#Route for login into existing account.
@app.route('/login', methods=['POST'])
def login():
    auth=request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not varify.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})

    user=User.query.filter_by(phone=auth.username).first()

    if not user:
        return make_response('Could not varify. There is no user with the given email id.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token= jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not varify. Kindly check the password and email are correct.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})



#This method is used for authentication check of the API which need authentication
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None

        if 'Authorization' in request.headers:
            token=request.headers['Authorization']

        if not token:
            return jsonify({'status':'400','message': "token is missing."})

        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()

        except:
            return jsonify({'status':'400','message': "token is Invalid!"})

        return f(current_user, *args, **kwargs)

    return decorated



# Route for sending the message
@app.route('/Send_Message', methods=['POST'])
@token_required
def Send_Message(current_user):
    try:
        current_user_id=current_user.id
        phone=current_user.phone
        data=request.get_json()
        to=data['to']
        message=data['message']

    except:
        return jsonify({"status": 400, "message": "Bad Request."})


    unique_id = User_Unique.query.filter_by(phone=phone).first().unique_id

    id='100'+str(current_user_id) + '10000' + str(unique_id)
    message=Messages(id=id, message_text=message,from_phone=phone,to_phone=to)
    db.session.add(message)
    db.session.commit()
    user_unique=User_Unique(phone=phone,unique_id=int(unique_id)+1)
    db.session.add(user_unique)
    db.session.commit()
    return jsonify({"status": 200, "message": "The message has been sent."})



# Route for getting the tickets with the limit
@app.route('/message', methods=['GET'])
@token_required
def Get_messages(current_user):
    try:
        current_user_id=current_user.id
        phone=current_user.phone
        data=request.get_json()
        to=data['to']
        per_page=data['per_page']
        page_no=data['page_no']
        start=per_page*page_no
        end=start+per_page
    except:
        return jsonify({"status": 400, "message": "Bad Request."})
    id_range='100'+str(current_user_id)+'10000'
    current_messages = Messages.query.filter((Messages.id.like(id_range)) | ((Messages.from_phone==to) & (Messages.to_phone==phone))).order_by(
    desc(Messages.time).slice(start,end).all()
    result = dict()
    data=dict()
    for message in current_messages:
            message_output = dict()
            message_output["Message"]=message.message_text
            message_output["from_phone"]=message.from_phone
            message_output["to_phone"]=message.to_phone
            message_output["time"]=message.time

            data[j] = message_output
            j+=1

        result["Messages"]=data

        return jsonify(result)
