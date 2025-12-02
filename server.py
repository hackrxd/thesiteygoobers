import os
import flask
import random
import bot.main as bot
import asyncio
import threading
import json
import sys
from flask import Flask, request, abort, send_file, send_from_directory, render_template

app = Flask(__name__, static_folder='static')

blocked_ips = []

@app.errorhandler(404)
def page_not_found(e):
    # Renders the 404.html template and explicitly sends a 404 status code
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbiddon(e):
    return render_template('403.html'), 403

@app.before_request
def block_probes():
    with open('blocked_ips.txt', 'r') as f:
        for line in f:
            blocked_ips.append(line)
    if request.remote_addr in blocked_ips and not request.path == "/main.css":
        abort(403)
    else:
        return send_file('main.css')
    if not request.method.isascii():
        blocked_ips.append(request.remote_addr)
        with open('blocked_ips.txt', 'a') as f:
            f.write(f"{request.remote_addr}\n")


@app.route('/', methods=['GET'])
def home():
    return flask.send_file('index.html')

@app.route('/main.css', methods=['GET'])
def styling():
    return flask.send_file('main.css', mimetype='text/css')

@app.route('/events/', methods=['GET'])
def events():
    return flask.send_file('events.html')

@app.route('/events/anonymous/', methods=['GET'])
def anonymous_event():
    return flask.send_file('anonymousanomaly.html')

@app.route('/members/', methods=['GET'])
def members():
    return flask.send_from_directory('members', 'index.html')

@app.route('/fuck', methods=['GET'])
def fuck():
    return "why did you think there would be something on this page??"

@app.route('/members/<folder_name>/', methods=['GET'])
def servemeber(folder_name):
    # Define the folder path where 'index.html' should exist
    folder_path = os.path.join('members', folder_name, 'index.html')

    # Check if the index.html file exists
    if os.path.exists(folder_path):
        return flask.send_from_directory(os.path.join('members', folder_name), 'index.html')
    else:
        return flask.abort(404)  # If the file doesn't exist, return 404



@app.route('/members/<folder_name>/<filename>', methods=['GET'])
def member_folder(folder_name, filename):
    # Handle if the request is for a .css file
    if filename.endswith('.css'):
        css_folder_path = os.path.join('members', folder_name, 'css')
        # Ensure the CSS file exists in the right subdirectory
        if os.path.exists(os.path.join(css_folder_path, filename)):
            return flask.send_from_directory(css_folder_path, filename)
        else:
            return flask.abort(404)  # If CSS file doesn't exist
    
    # Handle index.html or any other file
    folder_path = os.path.join('members', folder_name, 'index.html')

    if os.path.exists(folder_path):
        return flask.send_from_directory(os.path.join('members', folder_name), 'index.html')
    else:
        return flask.abort(404)  # Folder or index.html not found

@app.route('/api/cat')
def cat():
    cat_gifs = []
    # Use os.path.join for robust path construction
    cat_dir = os.path.join(app.root_path, 'static', 'cats') 
    for i in os.listdir(cat_dir):
        cat_gifs.append(i)
    # The external URL needs to be accessible, adjust the hostname/port if needed
    cat = random.choice(cat_gifs)
    fullcat = f"http://hackrai.duckdns.org:3000/static/cats/{cat}"
    return fullcat

def updateQuote(message, author):
    # Create a dictionary for the quote and author
    new_quote = {
        'message': message,
        'author': author
    }
    
    # Open the file and append the new quote
    try:
        # Try to read existing data from the JSON file
        with open('webtextdata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, start with an empty list
        data = []
    
    # Append the new quote to the existing list of quotes
    data.append(new_quote)
    
    # Write the updated list back to the file
    with open('webtextdata.json', 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/webtextdata', methods=['GET'])
def get_quotes():
    # Check if the JSON file exists
    if not os.path.exists('webtextdata.json'):
        return flask.jsonify([])  # Return empty list if file doesn't exist
    
    # Open and load the JSON data from the file
    try:
        with open('webtextdata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return flask.jsonify([])  # Return empty list in case of an error

    return flask.jsonify(data)


try:
    # 1. Function to run the Flask app (synchronous)
    def run_flask_app():
        # Set debug=False when using threading/production to avoid issues
        app.run(host='0.0.0.0', port=3000, debug=False) 
        # Use '0.0.0.0' to listen on all interfaces

    # 2. Main execution block
    if __name__ == '__main__':
        # a. Start the synchronous Flask server in a separate thread.
        print("Starting Flask server on a new thread...")
        server_thread = threading.Thread(target=run_flask_app)
        server_thread.start() # This function returns immediately

        # b. Start the asynchronous bot in the main thread.
        print("Starting bot in the main asyncio loop...")
        # NOTE: Your bot.start() must NOT call asyncio.run() internally.
        # It should only call the main bot function that starts the loop,
        # or just client.run_forever() if available.
        try:
            bot.start() 
        except Exception as e:
            print(f"Bot failed to start: {e}")
except KeyboardInterrupt:
    print("Exiting...")
    sys.exit()