import os
import flask

app = flask.Flask(__name__, static_folder='public')

@app.route('/', methods=['GET'])
def home():
    return flask.send_file('index.html')

@app.route('/main.css', methods=['GET'])
def styling():
    return flask.send_file('main.css', mimetype='text/css')

@app.route('/events', methods=['GET'])
def events():
    return flask.send_file('events.html')

@app.route('/events/anonymous', methods=['GET'])
def anonymous_event():
    return flask.send_file('anonymousanomaly.html')

@app.route('/members', methods=['GET'])
def members():
    return flask.send_file('members/index.html')


# Run the app
if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
