import os
import flask
import random

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


@app.route('/api/cat')
def cat():
    cat_gifs = []
    for i in os.listdir('public/cats'):
        cat_gifs.append(i)
    print(cat_gifs)
    cat = random.choice(cat_gifs)
    fullcat = f"http://hackrai.duckdns.org:3000/public/cats/{cat}"
    return fullcat

# Run the app
if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
