from flask import Flask, jsonify
from flask import request
from flask import abort, make_response

import sqlite3

app = Flask(__name__)

@app.route("/api/v1/info")
def home_index():
    conn = sqlite3.connect('mydb.db')
    api_list = []
    cursor = conn.execute('SELECT buildtime, version, methods, links from apirelease')
    for row in cursor:
        api = {}
        api['buildtime'] = row[0]
        api['version'] = row[1]
        api['methods'] = row[2]
        api['links'] = row[3]
        api_list.append(api)
    conn.close()
    return jsonify({'api_version': api_list}), 200

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'email': request.json['email'],
        'name': request.json['name'],
        'password': request.json['password'],
    }
    return jsonify({'status': add_user(user)}), 201

@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    if not request.json or not 'username' in request.json: abort(400)
    user = request.json['username']
    return jsonify({'status': del_user(user)}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = {}
    if not request.json: abort(400)
    user['id'] = user_id
    key_list = request.json.keys()
    for i in key_list:
        user[i] = request.json[i]
    print(user)
    return jsonify({'status': upd_user(user)}), 200

def upd_user(user):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = {0}".format(user['id']))
    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        key_list = user.keys()
        for i in key_list:
            if i != 'id':
                cursor.execute("UPDATE users SET {0} = '{1}' WHERE id = {2}".format(i, user[i], user['id']))
                conn.commit()
    return "Success"

def del_user(del_user):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username ='{0}'".format(del_user))
    data = cursor.fetchall()
    print("Data : {0}".format(data))
    if len(data) == 0:
        abort(404)
    else:
        cursor.execute("DELETE FROM users WHERE username = '{0}'".format(del_user))
        conn.commit()
        return "Success"

def add_user(new_user):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username='{0}' or email='{1}'".format(new_user['username'], new_user['email']))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute("INSERT INTO users(username, email, password, full_name) values ('{0}', '{1}', '{2}', '{3}')".format(new_user['username'], new_user['email'], new_user['password'], new_user['name']))
        conn.commit()
        return "success"
        conn.close()

@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)

@app.errorhandler(409)
def user_found(error):
    return make_response(jsonify({'error': 'Conflict: Record exist'}), 409)


def list_users():
    conn = sqlite3.connect('mydb.db')
    api_list = []
    cursor = conn.execute("SELECT username, full_name, email, password, id from users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['full_name'] = row[1]
        a_dict['email'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    conn.close()
    return jsonify({'user_list': api_list})

def list_user(user_id):
    conn = sqlite3.connect('mydb.db')
    api_list = []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users where id={0}'.format(user_id))
    data = cursor.fetchall()
    if len(data) == 0:
        abort(404)
    if len(data) != 0:
        user = {}
        user['username'] = data[0][0]
        user['email'] = data[0][1]
        user['password'] = data[0][2]
        user['full_name'] = data[0][3]
        user['id'] = data[0][4]
    conn.close()
    return jsonify(user)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)