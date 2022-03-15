import json
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from engineio.async_drivers import gevent
#from auth_decorator import login_required
from datetime import timedelta
from flask_socketio import SocketIO, send, emit
import binascii
import os
import database_helper
import sys


tokenDic = {
    "token": "",
    "email": ""
 }

webSocketConnection=[]

#####WEB SOCKET PART

app = Flask(__name__, template_folder='static')
app.debug = True
socketio = SocketIO(app)

@socketio.on('connect')
def websocketConnection():
    #print("Client establishing websocket connection")
    #socketio.send("signout")
    #send('Hello', to=request.sid)
    #print("hello there")
    if webSocketConnection:
        for e in webSocketConnection:
            print("e[0] is: ", e[0])
            print("email is: ", tokenDic["email"])
            print("Socket id is: ", request.sid)
            if(e[1]==tokenDic["email"]): #different token -> logout
                print("I'm HERE")
                webSocketConnection.remove(e)
                socketio.send("signout", to=e[0])

    webSocketConnection.append((request.sid, tokenDic["email"], tokenDic["token"]))

#token check

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

@app.route('/')
def index():
    return render_template('client.html') #render_template? or app.send_static_file


#@socketio.on('message')
#def handle_message(message):
    #print('received message: ' + message)

#@socketio.on('my event')
#def handle_my_custom_event(json):
    #emit('my response', json)


@app.route('/user/signup', methods = ['POST'])
def sign_up():
    json = request.get_json()
    if "email" in json and "password" in json and "firstname" in json and "familyname" in json and "gender" in json and "city" in json and "country" in json:
        if len(json['email']) < 30 and len(json['password']) > 5 and len(json['password']) < 30 and len(json['firstname']) < 30 and len(json['familyname']) < 30 and len(json['gender']) < 30 and len(json['city']) < 30 and len(json['country']) < 30:
            result = database_helper.create_user(json['email'], json['password'], json['firstname'], json['familyname'], json['gender'], json['city'], json['country'])
            if result == True:
                return "{}", 201
            else:
                return "{}", 409
        else:
            return "{}", 400
    else:
        return "{}", 400

@app.route('/user/signin', methods = ['POST'])
def sign_in():

    
    
    json = request.get_json()
    if "email" in json and "password" in json:
        if len(json['email']) < 30 and len(json['password']) < 30:
            result = database_helper.get_password(json['email'], json['password'])
            if result == True:
                token = binascii.hexlify(os.urandom(20)).decode()
                tokenDic["token"] = token
                tokenDic["email"] = json['email']
                
                print(webSocketConnection)
               
                database_helper.send_token(token)
                #jsonify token
                return jsonify({"token" : token}), 200
            else:
                return "{}", 404
        else:
            return "{}", 400
    else:
        return "{}", 400


@app.route('/user/changepassword', methods = ['PUT'])
def change_password():

    json = request.get_json()
    if "password" in json and "newpassword" in json:
        if len(json['password']) < 30 and len(json['newpassword']) < 30:
            result = database_helper.new_password(tokenDic["token"], json['password'], json['newpassword'])
            if result == True:
                return "{}", 201
            else:
                return "{}", 500
        else:
            print("1")
            return "{}", 400
    else:
        print("2")
        return "{}", 400

@app.route('/user/postmessage', methods = ['PUT'])
def post_message():

    
    json = request.get_json(force = True)
    print(json)
    
    result = database_helper.message_help(tokenDic['token'], json['message'], json['email'])
    if result == True:
        return "{}", 201
    else:
        return "{}", 500


@app.route('/user/getuserdatabytoken', methods = ['GET'])
def get_user_data_by_token():

    rows = database_helper.retrieve_data_token(tokenDic['token'])
    if rows != False:
        result = []
        for row in rows:
            result.append({"email": row[0], "firstname" : row[2], "familyname" : row[3], "gender" : row[4], "city" : row[5], "country" : row[6]})
        return jsonify(result), 200
    else:
        return "{}", 404


@app.route('/user/getuserdatabyemail/<email>', methods = ['GET'])
def get_user_data_by_email(email):


    rows = database_helper.retrieve_data_email(tokenDic['token'], email)
    if rows != False:
        result = []
        for row in rows:
            result.append({"email": row[0], "firstname" : row[2], "familyname" : row[3], "gender" : row[4], "city" : row[5], "country" : row[6]})
        return jsonify(result), 200
    else:
        return "{}", 404


@app.route('/user/getusermessagesbytoken', methods = ['GET'])
def get_user_messages_by_token():

    result = database_helper.retrieve_messages_token(tokenDic['token'])
    if result != False:
        #json_result = json.dumps(result, separators =(',', ':'))
        return jsonify({"messages" : result}), 200
    else:
        return "{}", 404


@app.route('/user/getusermessagesbyemail/<email>', methods = ['GET'])
def get_user_messages_by_email(email):

    rows = database_helper.retrieve_messages_email(tokenDic['token'], email)
    if rows != False:
        return jsonify({"messages" : rows}), 200
    else:
        return "{}", 500



@app.route('/user/checkuser', methods = ['POST'])
def check_user():

    json = request.get_json(force = True)
    print(json)
    result = database_helper.find_user_byemail(json)
    if result != False:
        return "{}", 200
    else:
        return "{}", 404
