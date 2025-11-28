import os
import flask

app = flask.Flask(__name__, static_folder='public')

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    return flask.send_from_directory(app.static_folder, filename)

@app.route('/', methods=['GET'])
def home():
    return flask.send_file('index.html')


@app.route('/main.css', methods=['GET'])
def styling():
    return flask.send_file('main.css', mimetype='text/css')

@app.route('/public/fonts', methods=['GET'])
def fonts():
    return flask.send_file('public/fonts', mimetype='font/ttf')

@app.route('/events', methods=['GET'])
def events():
    return flask.send_file('events.html')

app.run(host='localhost', port=3000)