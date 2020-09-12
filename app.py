from flask import Flask

app = Flask(__name__)

@app.route('/member', methods=['GET'])
def members():
    return None

@app.route('/member/<int:member_id>', methods=['GET'])
def member(member_id):
    return None

@app.route('/member', methods=['POST'])
def add_member():
    return None

@app.route('/member/<int:member_id>', methods=['PUT'])
def edit_member(member_id):
    return None

@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return None

if __name__ == "__main__":
    app.run(debug=True)