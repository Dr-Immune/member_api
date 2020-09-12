from flask import Flask

app = Flask(__name__)

@app.route('/members', methods=['GET'])
def members():
    return 'this is working'

if __name__ == "__main__":
    app.run(debug=True)