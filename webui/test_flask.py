from flask import Flask

a = Flask(__name__)

@a.route('/')
def hello_world():
    return '<p>hello world</p>'

a.run(host='0.0.0.0', port=12345, debug=True)

