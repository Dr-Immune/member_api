from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'member_api'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/member_api'
mysql = MySQL(app)
db = SQLAlchemy(app)

class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(10), nullable=False)    

    def __repr__(self):
        return '<user %r>' % self.name


class Users(db.Model):
    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<user %r>' % self.username


def authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth:
            received_username = auth.username
            received_password = auth.password

            user = Users.query.filter_by(username = received_username).first()
            if check_password_hash(user.password, received_password):
                return f(*args, **kwargs)
            return jsonify({"status": "authentication failed"}), 401
        return jsonify({"status": "no authentication parameters"}), 400
    return decorated


@app.route('/member', methods=['GET'])
@authentication
def members():
    result = db.session.query(Members.id, Members.name, Members.email, Members.level)

    json_result = []
    for item in result:
        json_result.append(item._asdict())

    return jsonify(json_result)

@app.route('/member/<int:member_id>', methods=['GET'])
@authentication
def member(member_id):
    result_count = Members.query.filter(Members.id == member_id).count()
    if result_count == 0:
        return Response('Member not found', status=404)

    result = db.session.query(Members.id, Members.name, Members.email, Members.level).filter(Members.id == member_id)
    json_result = []
    for item in result:
        json_result.append(item._asdict())

    return jsonify(json_result)

@app.route('/member', methods=['POST'])
@authentication
def add_member(): 
    data = request.get_json()
    new_member = data['new_member']
    name = new_member['name']
    email = new_member['email']
    level = new_member['level']

    new_member_query = Members(name=name, email= email, level=level)
    db.session.add(new_member_query)
    db.session.commit()

    result_count = Members.query.filter_by(name = name).count()
    if result_count == 0 :
        return Response('error', status=400)


    result = db.session.query(Members.id, Members.name, Members.email, Members.level).filter(Members.name == name)
    json_result = []
    for item in result:
        json_result.append(item._asdict())

    return jsonify(json_result), 201

@app.route('/member/<int:member_id>', methods=['PUT'])
@authentication
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    result_count = Members.query.filter(Members.id == member_id).count()
    if result_count == 0:
        return Response('User not found', status=404)

    user = Members.query.filter(Members.id == member_id).first()
    user.name = name
    user.email = email
    user.level = level
    db.session.commit()

    result = {"id": user.id, "name": user.name, "email": user.email, "level": user.level}

    return jsonify(result)

@app.route('/member/<int:member_id>', methods=['DELETE'])
@authentication
def delete_member(member_id):
    user_exist = Members.query.filter_by(id = member_id).count()
    if user_exist == 0:
        return Response('User not found', status=404)
    
    user = Members.query.filter_by(id = member_id).first()
    db.session.delete(user)
    db.session.commit()

    user_exist = Members.query.filter_by(id = member_id).count()
    if user_exist == 0:
        return Response('Member deletsed successfuly', status=200)
    return Response('Member not deleted')


@app.route('/user', methods=['POST'])
def add_user():
    new_user = request.get_json()
    username = new_user['username']
    password = new_user['password']
    hashed_password = generate_password_hash(password, method='sha256')

    user_exist = Users.query.filter_by(username = username).count()
    if user_exist == 1:
        return Response('User exist, try another username', status=400)

    new_user = Users(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    user_exist = Users.query.filter_by(username = username).count()
    if user_exist == 0:
        return Response('User not created', status=500)

    return jsonify({"status": "User created", "User": {"username": username, "password": password}})

@app.route('/checkuser', methods=['POST'])
def check_user():
    userinfo = request.get_json()
    username = userinfo['username']
    password = userinfo['password']

    user = Users.query.filter_by(username = username).first()
    check_result = check_password_hash(user.password, password)

    return jsonify(check_result)


if __name__ == "__main__":
    app.run(debug=True)