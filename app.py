from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'member_api'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth:
            received_username = auth.username
            received_password = auth.password
            cur = mysql.connection.cursor()
            cur.execute('SELECT password FROM users WHERE username = %s', [received_username])
            result = cur.fetchone()

            if check_password_hash(result['password'], received_password):
                return f(*args, **kwargs)
            return jsonify({"status": "authentication failed"}), 401
        return jsonify({"status": "no authentication parameters"}), 400
    return decorated


@app.route('/member', methods=['GET'])
@authentication
def members():
    cur = mysql.connect.cursor()
    cur.execute('SELECT * FROM members')
    result = cur.fetchall()

    return jsonify(result)

@app.route('/member/<int:member_id>', methods=['GET'])
@authentication
def member(member_id):
    cur = mysql.connect.cursor()
    cur.execute('SELECT * FROM members WHERE id = %s', [member_id])
    result = cur.fetchone()

    if result == None:
        print('str')
        return Response('Member not found', status=404)
    return jsonify(result)

@app.route('/member', methods=['POST'])
@authentication
def add_member():
    cur = mysql.connection.cursor()
    data = request.get_json()
    new_member = data['new_member']
    name = new_member['name']
    email = new_member['email']
    level = new_member['level']

    cur.execute('INSERT INTO members(name, email, level) VALUES(%s, %s, %s)', [name, email, level])
    mysql.connection.commit()

    cur.execute('SELECT * FROM members WHERE name = %s ', [name])
    result = cur.fetchone()

    if result == None:
        return Response('error', status=400)
        # TODO: RETURN PROPER MESSAGE
    else:
        return jsonify(result), 201

@app.route('/member/<int:member_id>', methods=['PUT'])
@authentication
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    cur = mysql.connect.cursor()
    cur.execute('SELECT name FROM members WHERE id = %s', [member_id])
    check_result = cur.fetchone()
    if check_result == None:
        return Response('User not found', status=404)
        
    cur.execute('UPDATE members SET name = %s, email = %s, level = %s WHERE id = %s', [name, email, level, member_id])
    cur.connection.commit()

    cur.execute('SELECT id, name, email, level FROM members WHERE id = %s', [member_id])
    result = cur.fetchone()

    return jsonify(result)

@app.route('/member/<int:member_id>', methods=['DELETE'])
@authentication
def delete_member(member_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT name FROM members WHERE id = %s', [member_id])
    check_result = cur.fetchone()
    if check_result == None:
        return Response('User not found', status=404)
    cur.execute('DELETE FROM members WHERE id = %s', [member_id])
    cur.connection.commit()
    return Response('Member deleted successfuly', status=200)

@app.route('/user', methods=['POST'])
def add_user():
    new_user = request.get_json()
    username = new_user['username']
    password = new_user['password']
    hashed_password = generate_password_hash(password, method='sha256')

    cur = mysql.connect.cursor()
    cur.execute('SELECT username FROM users WHERE username = %s', [username])
    result = cur.fetchone()

    if result != None:
        return Response('User exist, try another username', status=400)

    cur.execute('INSERT INTO users(username, password) VALUES(%s, %s)', [username, hashed_password])
    cur.connection.commit()

    cur.execute('SELECT username FROM users WHERE username = %s', [username])
    result = cur.fetchone()

    if result == None:
        return Response('User not created', status=500)

    return jsonify({"status": "User created", "User": {"username": username, "password": password}})

@app.route('/checkuser', methods=['POST'])
def check_user():
    userinfo = request.get_json()
    username = userinfo['username']
    password = userinfo['password']

    cur = mysql.connect.cursor()
    cur.execute('SELECT username, password FROM users WHERE username = %s', [username])
    result = cur.fetchone()
    
    check_result = check_password_hash(result['password'], password)

    return jsonify(check_result)


if __name__ == "__main__":
    app.run(debug=True)