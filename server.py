from flask import Flask, Response, request, jsonify #added to top of file
from flask_cors import CORS #added to top of file
import sqlite3

#Notes for user:

# Get all users by rank
# http://127.0.0.1:8000/api/scores/

# Get single user by score rank
# http://127.0.0.1:8000/api/scores/<id>

# Add / Update user score record
# http://127.0.0.1:8000/api/scores/add

# Get users by id
#http://127.0.0.1:8000//api/scores/users/<id>

# Get all Users
#http://127.0.0.1:8000//api/scores/users/


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE scores (
                id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            );
        ''')

        conn.commit()
        print("User table created successfully")
    except:
        print("User table creation failed - Maybe table")
    finally:
        conn.close()

create_db_table()

def insert_score(score):
    inserted_user = {}
    user = {}

    try:
        conn = connect_to_db()
        cur = conn.cursor()

        usernamecheck = cur.execute("SELECT COUNT(id) FROM scores WHERE name=?;", [score['name']])

        usernamecheck = cur.fetchone()

        if usernamecheck[0] != 0:
            
            user_id = get_score_by_name(score['name'])
            print(user_id, flush=True)
 
            # convert row object to dictionary
            user["id"] = user_id["id"]
            user["name"] = score["name"]
            user["score"] = score["score"]

            print(user, flush=True)

            return update_user(user)
        
        cur.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (score['name'],   
                    score['score']) )
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_user

def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM scores")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["id"] = i["id"]
            user["name"] = i["name"]
            user["score"] = i["score"]
            
            users.append(user)

    except:
        users = []

    return users

def get_users_ranked():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM `scores` ORDER BY `score` DESC")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["id"] = i["id"]
            user["name"] = i["name"]
            user["score"] = i["score"]
            
            users.append(user)

    except:
        users = []

    return users

def get_score_by_name(name):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM scores WHERE name = ?", 
                       (name,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["id"] = row["id"]
        user["name"] = row["name"]
        user["score"] = row["score"]

    except:
        user = {}

    return user


def get_user_by_id(id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM scores WHERE id = ?", 
                       (id,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["id"] = row["id"]
        user["name"] = row["name"]
        user["score"] = row["score"]

    except:
        user = {}

    return user

def get_score_by_rank(rank):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        totalScoresCount = cur.execute("SELECT COUNT(id) FROM scores;")
        totalScoresCount = cur.fetchone()

        print(totalScoresCount[0], flush=True)
        print(rank[0], flush=True)
        print(int(rank) > int(totalScoresCount[0]), flush=True)
        
   
        if int(rank) > int(totalScoresCount[0]):
                return "Record does not exist"

        cur.execute("SELECT * FROM `scores` ORDER BY `score` DESC LIMIT 1 OFFSET ?", 
                       ((int(rank) - (1)),))
        row = cur.fetchone()

        # convert row object to dictionary
        user["id"] = row["id"]
        user["name"] = row["name"]
        user["score"] = row["score"]

    except:
        user = {}

    return user

def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE scores SET name = ?, score = ? WHERE id =?",  
                     (user["name"], user["score"], user["id"],))
        conn.commit()
        #return the user
        updated_user = get_user_by_id(user["user_id"])

    except:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()

    return updated_user

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#Get a score by rank
@app.route('/api/scores/<id>', methods=['GET'])
def api_get_score_by_rank(id):
    return jsonify(get_score_by_rank(id))

@app.route('/api/scores/users/', methods=['GET'])
def api_get_users_users():
    return jsonify(get_users())

@app.route('/api/scores/', methods=['GET'])
def api_get_users():
    return jsonify(get_users_ranked())

@app.route('/api/scores/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route('/api/scores/add',  methods = ['POST'])
def api_add_score():
    user = request.get_json()
    return jsonify(insert_score(user))

@app.route('/api/scores/update',  methods = ['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))

if __name__ == "__main__":
    port = 8000
    #app.debug = True
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=port) #run app

