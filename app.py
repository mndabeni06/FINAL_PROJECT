# ----------Masimthembe Ndabeni FINAL PROJECT--------#

import hmac
import sqlite3
import cloudinary


from flask_mail import Mail as Mail, Message
from flask import Flask, request, redirect
from flask_cors import CORS, cross_origin
from flask_jwt import JWT, jwt_required
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError
import cloudinary
import cloudinary.uploader


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


# Creating player_registration table
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


# Creating player_login table
def init_player_login_table():
    with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS player_login (player_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "username TEXT NOT NULL,"
                     "password TEXT NOT NULL)")
    print("players_login table created successfully.")


# Creating player_profile table
def init_player_profile_table():
    with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS players_profiles (player_id INTEGER PRIMARY KEY AUTOINCREMENT,"
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


def image_upload():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name="life-choices", api_key="567289268154448",
                      api_secret="kBQ-7vVF1p3S6yHq84hTAiH5AyE")
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        profile_image = request.form['image']
        app.logger.info('%s file_to_upload', profile_image)
        if profile_image:
            upload_result = cloudinary.uploader.upload(profile_image)
            app.logger.info(upload_result)
            return upload_result['url']


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
            new_data.append(User(data[0], data[1], data[2], data[3], data[4], data[5]))
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
@app.route('/', methods=["GET"])
@cross_origin()
def welcome():
    response = {}
    if request.method == "GET":
        response["message"] = "Welcome"
        response["status_code"] = 201
        return response


# Fetching ALL PLAYER FROM REGISTRATION
@app.route('/get_all_players/', methods=["GET"])
@cross_origin()
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
@cross_origin()
def player_login():
    response = {}

    if request.method == "POST":
        try:
            username = request.json["username"]
            password = request.json["password"]

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
@cross_origin()
def player_registration():
    response = {}
    if request.method == "POST":
        try:
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            email = request.json['email']
            username = request.json['username']
            password = request.json['password']
            home_address = request.json['home_address']
            contact_number = request.json['contact_number']

            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO player_reg("
                               "first_name,"
                               "last_name,"
                               "email,"
                               "username,"
                               "password,"
                               "home_address,"
                               "contact_number) VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (first_name, last_name, username, email, password, home_address, contact_number))
                conn.commit()
                response["message"] = "new player successfully registered"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to registered"
            response["status_code"] = 400
            return response


# ROUTE TO SEND AN EMAIL TO REGISTERED PLAYER
@app.route('/send_email/<email>', methods=['GET'])
@cross_origin()
def send_email(email):
    mail = Mail(app)

    msg = Message('Hello Message', sender='mndabeni6@gmail.com.com', recipients=[email])
    msg.body = "This is the email body after making some changes"
    mail.send(msg)

    return "Thank you for registering at Soccer Talent Hub."


# GETTING REGISTERED  PLAYER BY PLAYER_ID
@app.route('/get_player/<int:player_id>', methods=["GET"])
@cross_origin()
def get_registered_player(player_id):
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
@cross_origin()
def get_all_profiles():
    response = {}

    if request.method == "GET":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players_profiles")
            profiles = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = profiles
        return response


# GETTING A SINGLE PLAYER PROFILE
@app.route('/each_profile/<int:player_id>/', methods=["GET"])
@cross_origin()
def get_each_profile(player_id):
    response = {}

    if request.method == "GET":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players_profiles WHERE player_id=" + str(player_id))
            profile = cursor.fetchone()

        response['status_code'] = 200
        response['data'] = profile
        return response


# get user by password
@app.route('/player-info/<username>', methods=["GET"])
@cross_origin()
def get_player_password(username):
    response = {}
    with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM player_reg WHERE password=?", [username])
        user = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = user  # tuple(accumulator)
    return response


# CREATING A NEW PLAYER PROFILE
@app.route('/create_profile/', methods=["POST"])
@cross_origin()
def create_profile():
    response = {}
    if request.method == "POST":
        try:
            full_name = request.form['full_name']
            nickname = request.form['nickname']
            date_of_birth = request.form['date_of_birth']
            age = request.form['age']
            citizenship = request.form['citizenship']
            position = request.form['position']
            place_of_birth = request.form['place_of_birth']
            current_club = request.form['current_club']


            with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO players_profiles ("
                               "full_name, "
                               "nickname, "
                               " date_of_birth,"
                               "age,"
                               "citizenship,"
                               "place_of_birth,"
                               "position,"
                               "current_club,"
                               "image)  VALUES (?, ?, ?,?, ?, ?, ?, ?, ?, ?)",
                               (full_name, nickname, date_of_birth, age, citizenship, place_of_birth,
                                position, current_club, image_upload()))
                conn.commit()
                response["message"] = "New player has been successfully added to database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to create player_profiles"
            response["status_code"] = 400
            return response


# UPDATING REGISTERED PLAYERS
@app.route('/update_player_registration/<int:player_id>', methods=["PUT"])
@cross_origin()
def update_player_registration(player_id):
    response = {}
    
    if request.method == "PUT":
        with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
            incoming_data = dict(request.form)

            put_data = {}

            # UPDATING A FIRST_NAME
            if incoming_data.get("first_name") is not None:
                put_data["first_name"] = incoming_data.get("first_name")
                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET first_name =? WHERE player_id=?",
                                   (put_data["first_name"], player_id))
                    conn.commit()
                    response['message'] = "first_name updated successfully"
                    response['status_code'] = 200

            # UPDATING LAST NAME
            if incoming_data.get("last_name") is not None:
                put_data['last_name'] = incoming_data.get('last_name')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET last_name =? WHERE player_id=?",
                                   (put_data["last_name"], player_id))
                    conn.commit()

                    response["content"] = "last name updated successfully"
                    response["status_code"] = 200

            # UPDATING EMAIL
            if incoming_data.get("email") is not None:
                put_data['email'] = incoming_data.get('email')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET email =? WHERE player_id=?",
                                   (put_data["email"], player_id))
                    conn.commit()

                    response["content"] = "email updated successfully"
                    response["status_code"] = 200

            # UPDATING USERNAME
            if incoming_data.get("username") is not None:
                put_data['username'] = incoming_data.get('username')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET username =? WHERE player_id=?", (put_data["username"], player_id))
                    conn.commit()

                    response["content"] = "username updated successfully"
                    response["status_code"] = 200

            # UPDATING PASSWORD
            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')
                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET password =? WHERE player_id=?",
                                   (put_data["password"], player_id))
                    conn.commit()

                    response["content"] = "password updated successfully"
                    response["status_code"] = 200

            # UPDATING CONTACT NUMBER
            if incoming_data.get("contact_number") is not None:
                put_data['contact_number'] = incoming_data.get('contact_number')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET contact_number =? WHERE player_id=?",
                                   (put_data["contact_number"], player_id))
                    conn.commit()

                    response["content"] = "Contact number updated successfully"
                    response["status_code"] = 200

            # UPDATING HOME ADDRESS
            if incoming_data.get("home_address") is not None:
                put_data['home_address'] = incoming_data.get('home_address')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE player_reg SET home_address =? WHERE player_id=?",
                                   (put_data["home_address"], player_id))
                    conn.commit()

                    response["content"] = "home_address updated successfully"
                    response["status_code"] = 200

            return response


# UPDATING PLAYER PROFILE
@app.route('/update_profile/<int:player_id>', methods=["PUT"])
@cross_origin()
def update_player_profile(player_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
            incoming_data = dict(request.form)

            put_data = {}

            # UPDATING A FULL_NAME
            if incoming_data.get("full_name") is not None:
                put_data["full_name"] = incoming_data.get("full_name")
                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET full_name =? WHERE player_id=?",
                                   (put_data["full_name"], player_id))
                    conn.commit()
                    response['message'] = "full_name updated successfully"
                    response['status_code'] = 200

            # UPDATING NICKNAME
            if incoming_data.get("nickname") is not None:
                put_data['nickname'] = incoming_data.get('nickname')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET nickname =? WHERE player_id=?",
                                   (put_data["nickname"], player_id))
                    conn.commit()

                    response["content"] = "nickname updated successfully"
                    response["status_code"] = 200

            # UPDATING PLACE OF BIRTH
            if incoming_data.get("place_of_birth") is not None:
                put_data['place_of_birth'] = incoming_data.get('place_of_birth')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET place_of_birth =? WHERE player_id=?",
                                   (put_data["place_of_birth"], player_id))
                    conn.commit()

                    response["content"] = "Place of birth updated successfully"
                    response["status_code"] = 200

            # UPDATING AGE
            if incoming_data.get("age") is not None:
                put_data['age'] = incoming_data.get('age')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET age =? WHERE player_id=?", (put_data["age"], player_id))
                    conn.commit()

                    response["content"] = "player age updated successfully"
                    response["status_code"] = 200

            # UPDATING A DATE OF BIRTH
            if incoming_data.get("date_of_birth") is not None:
                put_data['date_of_birth'] = incoming_data.get('date_of_birth')
                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET date_of_birth =? WHERE player_id=?",
                                   (put_data["date_of_birth"], player_id))
                    conn.commit()

                    response["content"] = "Date of birth updated successfully"
                    response["status_code"] = 200

            # UPDATING CITIZENSHIP
            if incoming_data.get("citizenship") is not None:
                put_data['citizenship'] = incoming_data.get('citizenship')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET citizenship =? WHERE player_id=?",
                                   (put_data["citizenship"], player_id))
                    conn.commit()

                    response["content"] = "Player citizenship updated successfully"
                    response["status_code"] = 200

            # UPDATING POSITION
            if incoming_data.get("position") is not None:
                put_data['position'] = incoming_data.get('position')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET position =? WHERE player_id=?",
                                   (put_data["position"], player_id))
                    conn.commit()

                    response["content"] = "Player position updated successfully"
                    response["status_code"] = 200

            # UPDATING CURRENT POSITION
            if incoming_data.get("current_club") is not None:
                put_data['current_club'] = incoming_data.get('current_club')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET current_club =? WHERE player_id=?",  (put_data["current_club"], player_id))

                    conn.commit()

                    response["content"] = "Current Club updated successfully"
                    response["status_code"] = 200

            # UPDATING PLAYER IMAGE
            if incoming_data.get("image") is not None:
                put_data['image'] = incoming_data.get('image')

                with sqlite3.connect('Soccer_Talent_Hub.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE players_profiles SET image =? WHERE player_id=?",  (put_data["image"], player_id))

                    conn.commit()

                    response["content"] = "Player image updated successfully"
                    response["status_code"] = 200

            return response


# DELETE REGISTERED PLAYER
@app.route('/delete-registered-player/<int:player_id>', methods=["PUT"])
@cross_origin()
def delete_registered_player(player_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players_reg WHERE player_id=" + str(player_id))
            conn.commit()
            response['status_code'] = 200
            response['message'] = "registered player deleted successfully."
        return response


# DELETE PLAYER PROFILE
@app.route('/delete-profile/<int:player_id>', methods=["PUT"])
@cross_origin()
def delete_player_profile(player_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect("Soccer_Talent_Hub.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players_profiles WHERE player_id=" + str(player_id))
            conn.commit()
            response['status_code'] = 200
            response['message'] = "player profile deleted successfully."
        return response


if __name__ == '__main__':
    app.run(debug=True)
