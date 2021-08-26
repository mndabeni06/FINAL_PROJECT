#----------Masimthembe Ndabeni FINAL PROJECT--------#

import hmac
import sqlite3

from flask_mail import Mail as Mail
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from flask_jwt import JWT, jwt_required, current_identity

from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError


# Function to  create dictionaries in SQL rows, and data follows JSON format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Defining user authentication
class User(object):
    def __init__(self, player_id, username, password, email, contact_number, home_address):
        self.player_id = player_id
        self.username = username
        self.password = password
        self.email = email
        self.phone_number = contact_number
        self.address = home_address


# Creating players_registration table
def init_player_reg_table():
    conn = sqlite3.connect('Soccer_Talent_Hub.db')
    print("Database opened successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS player_reg (player_id INTEGER PRIMARY KEY AUTOINCREMENT,"    
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL, home_address TEXT NOT NULL, contact_number INT NOT NULL, email TEXT NOT NULL)")
    print("players_reg table created successfully")
    conn.close()


# Creating players_login table
def init_player_login_table():
    with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS player_login (player_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "username TEXT NOT NULL,"
                     "password TEXT NOT NULL)")
    print("players_login table created successfully.")


# Creating player_profile table
def init_player_profile_table():
    with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS player_profiles (player_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "full_name TEXT NOT NULL,"
                     "nickname INTEGER NOT NULL,"
                     "date_of_birth TEXT NOT NULL,"
                     "place_of_birth TEXT NOT NULL,"
                     "age INT NOT NULL,"
                     "image TEXT NOT NULL," 
                     "citizenship TEXT NOT NULL,"
                     "position TEXT NOT NULL,"
                     "current_club TEXT NOT NULL)")
    print("player_profile table created successfully")


# Defining Tables

init_player_reg_table()
init_player_login_table()
init_player_profile_table()


# Function to fetch everything from registration table
def fetch_player_reg():
    with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM player_reg")

        player_reg = cursor.fetchall()

        new_data = []

        for data in player_reg:
            new_data.append(User(data[0], data[3], data[4], data[5], data[6], data[7]))
    return new_data


users = fetch_player_reg()


username_table = {u.username: u for u in users}
userid_table = {u.player_id: u for u in users}


# authentication of username and password to get access token
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

# Defining Email Verification
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sithandathuzipho@gmail.com'
app.config['MAIL_PASSWORD'] = 'Crf6ZS@#'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
Mail = Mail(app)

jwt = JWT(app, authenticate, identity)


# Defining routes
@jwt_required
@app.route('/', methods=["GET"])
def welcome():
    response = {}
    if request.method == "GET":
        response["message"] = "Welcome"
        response["status_code"] = 201
        return response


# Fetching ALL PLAYER FROM REGISTRATION
@app.route('/get_all_players/', methods=["GET"])
def get_all():
    response = {}

    if request.method == "GET":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_reg")
            user = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = user
        return response


# PLAYER LOGIN
@app.route('/player_login/', methods=["POST"])
def player_login():
    response = {}

    if request.method == "POST":
     try:
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("INSERT INTO player_login("
                           "username,"
                           "password) VALUES(?, ?)", (username, password))

        response['status_code'] = 200
        response['message'] = "success"
        return response
     except ValueError:
            response["message"] = "Please enter correct details"
            response["status_code"] = 400
            return response


# PLAYER REGISTRATION
@app.route('/player_reg/', methods=["POST"])
def player_registration():
    response = {}
    if request.method == "POST":
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            home_address = request.form['home_address']
            contact_number = request.form['contact_number']

            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO player_reg("
                               "first_name,"
                               "last_name,"
                               "email,"
                               "username,"
                               "password,"
                               "home_address,"
                               "contact_number) VALUES(?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, username, email, password, home_address, contact_number))
                conn.commit()
                response["message"] = "new player successfully added  to database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 400
            return response


# GETTING A PLAYER BY PLAYER_ID
@app.route('/get_player/<int:player_id>', methods=["GET"])
def get_player(player_id):
    response = {}
    with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM player_reg WHERE player_id=" + str(player_id))

        user = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = user
    return response


# GETTING ALL PLAYER PROFILES
@app.route('/player_profiles/', methods=["GET"])
def get_all_profiles():
    response = {}

    if request.method == "GET":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_profiles")
            profiles = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = profiles
        return response


# GETTING A SINGLE PLAYER PROFILE
@app.route('/each_profile/ <int:player_id>', methods=["GET"])
def get_each_profile(player_id):
    response = {}

    if request.method == "GET":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_profiles")
            profile = cursor.fetchone()

        response['status_code'] = 200
        response['data'] = profile
        return response


# CREATING A NEW PLAYER PROFILE
@app.route('/create_profile/', methods=["POST"])
def create_profile():
    response = {}
    if request.method == "POST":
        try:
            player_id = request.form['player_id']
            full_name = request.form['full_name']
            nickname = request.form['nickname']
            date_of_birth = request.form['date_of_birth']
            age = request.form['age']
            citizenship = request.form['citizenship']
            position = request.form['position']
            place_of_birth = request.form['place_of_birth']
            current_club = request.form['current_club']
            image = request.form['image']

            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO player_profiles ("
                               "player_id, "
                               "full_name, "
                               "nickname, "
                               " date_of_birth,"
                               "age,"
                               "citizenship,"
                               "place_of_birth,"
                               "position,"
                               "current_club," 
                                "image)  VALUES (?, ?, ?,?, ?, ?, ?, ?, ?, ?)",
                               (player_id, full_name, nickname, date_of_birth, age, citizenship, place_of_birth, position, current_club, image))
                conn.commit()
                response["message"] = "New player has been successfully added to database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to create player_profiles"
            response["status_code"] = 400
            return response


# UPDATING PLAYER PROFILE
@app.route('/update_profile/<int:player_id>', methods=["PUT"])
def update_player_profile(player_id):
    response = {}

    if request.method == "PUT":
        try:
            player_id = request.form['player_id']
            full_name = request.form['full_name']
            nickname = request.form['nickname']
            date_of_birth = request.form['date_of_birth']
            age = request.form['age']
            citizenship = request.form['citizenship']
            place_of_birth = request.form['place_of_birth']
            position = request.form['position']
            image = request.form['image']
            current_club = request.form['current_club']

            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE player_profiles SET player_id=? AND full_name=?, AND nickname=?, AND date_of_birth=?, AND age=?, AND citizenship=? AND place_of_birth=? AND image=? AND position=? WHERE current_club=? "
                               , (player_id, full_name, nickname, date_of_birth, image, age, citizenship,place_of_birth, position, current_club))
                conn.commit()
                response["message"] = "Player profile  was successfully updated"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to update player_profile"
            response["status_code"] = 400
            return response


# DELETE PLAYER PROFILE
@app.route('/delete-profile/<int:player_id>', methods=["PUT"])
def delete_player_profile(player_id):
    response = {}

    if request.method == "PUT":
        try:
            player_id = request.form['player_id']
            full_name = request.form['full_name']
            nickname = request.form['nickname']
            date_of_birth = request.form['date_of_birth']
            age = request.form['age']
            citizenship = request.form['citizenship']
            place_of_birth = request.form = ['place_of_birth']
            position = request.form['position']
            image = request.form['image']
            current_club = request.form['current_club']

            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE player_profiles SET player_id=? AND full_name=?, AND nickname=?, AND date_of_birth=?, AND age=?, AND citizenship=? AND place_of_birth=?, AND image=? AND position=? AND current_club=? "
                               , (player_id, full_name, nickname, date_of_birth, image, age, citizenship,place_of_birth, position, current_club))
                conn.commit()
                response["message"] = "Player profile  was successfully deleted"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to delete player_profile"
            response["status_code"] = 400
            return response


if __name__ == '__main__':
    app.run(debug=True)
