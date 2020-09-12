from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'member_api'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/member', methods=['GET'])
def members():
    return None

@app.route('/member/<int:member_id>', methods=['GET'])
def member(member_id):
    return None

@app.route('/member', methods=['POST'])
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
def edit_member(member_id):
    return None

@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return None

if __name__ == "__main__":
    app.run(debug=True)