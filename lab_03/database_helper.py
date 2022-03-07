import sqlite3
from flask import g

DATABASE_URI = 'database.db'

loggedInUser = {
    "token": "",
    "email": ""
 }

def token_to_email(token):
    return loggedInUser["email"]

def send_token(token):
    loggedInUser["token"] = token


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)

    return db

def disconnect_db():
    db = getattr(g, 'db', None)

    if db is not None:
        db.close
        g.db = None

def create_user(email, password, firstname, familyname, gender, city, country):
    try:
        get_db().execute("insert into user values(?,?,?,?,?,?,?)", [email, password, firstname, familyname, gender, city, country])

        get_db().commit()
        return True
    except:  #FIX Exception

        return False



def get_password(email, password):

    loggedInUser["email"] = email
    cursor = get_db().execute("select * from user where user.email = ? and password = ?", [email, password])
    rows = cursor.fetchall()
    cursor.close()
    print(rows)
    if rows:
        return True
    else:
        return False

def find_user_byemail(email):

    cursor = get_db().execute("select * from user where email = ?", [email])
    rows = cursor.fetchall()
    cursor.close()
    print(rows)
    if rows:
        return True
    else:
        return False



def new_password(token, password, newpassword):

    try:
        get_db().execute("update user set password = ? where password = ?", [newpassword,password])
        get_db().commit()
        return True
    except:
        return False



def message_help(token, message, email):

    cursor = get_db().execute("select * from user where email = ?", [email])
    rows = cursor.fetchall()
    cursor.close()
    if rows: #user exists
        get_db().execute("insert into messages values(?, ?)", [message, email])
        get_db().commit()
        print(message)
        return True
    else:
        return False

def retrieve_data_token(token):

    email = token_to_email(token)
    cursor = get_db().execute("select * from user where user.email = ?", [email])
    rows = cursor.fetchall()
    cursor.close()
    print(rows)
    if rows:
        return rows
    else:
        return False

def retrieve_data_email(token, email):
    try:
        cursor = get_db().execute("select * from user where email = ?", [email])
        rows = cursor.fetchall()
        cursor.close()
        print(rows)
        return rows
    except sqlite3.DatabaseError as err:
        print(err)
        return False

def retrieve_messages_token(token):

    email = token_to_email(token)
    cursor = get_db().execute("select * from messages where email = ?", [email])
    rows = cursor.fetchall()
    cursor.close()
    print(rows)
    if rows:
        return rows
    else:
        return False

def retrieve_messages_email(token, email):


    cursor = get_db().execute("select * from messages where email = ?", [email])
    rows = cursor.fetchall()
    cursor.close()
    print(rows)
    if rows:
        return rows
    else:
        return False
