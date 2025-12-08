import os
import flask
import random
import bot.mainbeta as bot
import asyncio
import threading
import json
import sys
from flask import Flask, request, abort, send_file, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename


app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'

maintenence = True
newUI = False

def block_ip(ip):
    with open('blocked_ips.txt', 'a') as f:
        f.write(f"{ip}\n")


@app.errorhandler(404)
def page_not_found(e):
    # Renders the 404.html template and explicitly sends a 404 status code
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbiddon(e):
    return render_template('403.html'), 403

@app.errorhandler(400)
def badreq(e):
    return render_template('400.html'), 400

@app.errorhandler(500)
def error(e):
    return render_template('500.html'), 500

@app.before_request
def before():
    global newUI
    newUI = False
    if (
        maintenence
        and request.path not in ['/error', '/main.css']
        and request.remote_addr not in ["127.0.0.1", "192.168.1.60", "162.221.131.48"]
    ):
        return flask.redirect('/error')

    elif request.path == '/error':
        pass
    elif request.path == '/main.css':
        return flask.send_file('main.css')
    else:
        blocked_ips = []
        with open('blocked_ips.txt', 'r') as f:
            for line in f:
                blocked_ips.append(line.strip())
        if request.remote_addr in blocked_ips and not request.path == "/main.css":
            abort(403)
        elif request.remote_addr in blocked_ips and request.path == "/main.css":
            return send_file('main.css')
        if not request.method.isascii():
            block_ip(request.remote_addr)
        malicious_patterns = [
            "wget%20",   
            "%20sh",      
            "|",
            ";",
            "nc%20",    
            "rm%20-rf",   
            "etc/passwd",
            "mstshash=Administr",
            "\\x02\\x01\\x00",
            "/_next/",
            "\\x00"
        ]

        full_url = request.full_path

        for i in malicious_patterns:
            if i in full_url:
                block_ip(request.remote_addr)
                abort(400)
        newUIaddrs = []
        with open('newui.txt', 'r') as f:
            for line in f:
                newUIaddrs.append(line.strip())
        if request.remote_addr in newUIaddrs:
            newUI = True

@app.route('/', methods=['GET'])
def home():
    if newUI:
        return flask.send_file('newindex.html')
    return flask.send_file('index.html')

@app.route('/main.css', methods=['GET'])
def styling():
    return flask.send_file('main.css', mimetype='text/css')

@app.route('/events/', methods=['GET'])
def events():
    return flask.send_from_directory('events', 'index.html')

@app.route('/events/annual/<filename>', methods=['GET'])
def serveAnnual(filename):
    file = f"{filename}.html"
    return flask.send_from_directory('events/annual', file)

@app.route('/events/anonymous/', methods=['GET'])
def anonymous_event():
    return flask.send_file('anonymousanomaly.html')

@app.route('/members/', methods=['GET'])
def members():
    return flask.send_from_directory('members', 'index.html')

@app.route('/fuck', methods=['GET'])
def fuck():
    return "why did you think there would be something on this page??"

@app.route('/files')
def indexFile():
    return send_from_directory('files', 'index.html')

FILES_DIR = "files"  # base directory on disk

@app.route("/files/<path:filepath>")
def serve_files(filepath):
    full_path = os.path.join(FILES_DIR, filepath)

    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(FILES_DIR, filepath)

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
    
@app.route('/upload', methods=['GET'])
def uploadPage():
    return send_file('upload.html')


    
@app.route('/error', methods=['GET'])
def maintenenceredir():
    if not maintenence:
        return flask.redirect('/')
    return send_file('error.html')

@app.route('/api/cat')
def cat():
    if request.remote_addr == "127.0.0.1":
        cat_gifs = []
        # Use os.path.join for robust path construction
        cat_dir = os.path.join(app.root_path, 'static', 'cats') 
        for i in os.listdir(cat_dir):
            cat_gifs.append(i)
        # The external URL needs to be accessible, adjust the hostname/port if needed
        cat = random.choice(cat_gifs)
        fullcat = f"http://hackrai.duckdns.org:3000/static/cats/{cat}"
        return fullcat
    else:
        abort(403)

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

@app.route('/<filename>')
def serve_file(filename):
    if not os.path.exists(filename):
        abort(404)
    blockedfiles = [
        ".env"
    ]
    if filename in blockedfiles:
        abort(403)
    else:
        return send_file(filename)
    
@app.route('/uploads/<filename>')
def showupload(filename):
    return send_from_directory('uploads', filename)

@app.route('/ui/new')
def newUI():
    with open('newui.txt', 'a') as f:
        f.write(f"{request.remote_addr}\n")
        return flask.redirect('/')

@app.route('/ui/old')
def oldUI():
    with open('newui.txt', 'r') as f:
        uiaddrs = []
        for l in f:
            uiaddrs.append(l.strip())
        uiaddrs.remove(request.remote_addr)
        with open('newui.txt', 'w') as f:
                for i in uiaddrs:
                    f.write(f"{i}\n")
    return flask.redirect('/')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "File not found in request."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected by user."}), 400

    safe_name = secure_filename(file.filename)
    filename = f"{random.randint(1000000, 100000000)}-{random.randint(1000000, 100000000)}-{safe_name}".lower()
    file_url = f'/uploads/{filename}'
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(path)
    except Exception as e:
        print(f"Failed to save file to {path}: {e}")
        return jsonify({"error": "Upload failed."}), 500

    return jsonify({
        "originalName": file.filename,
        "storedName": filename,
        "fileUrl": file_url,
        "uploader": "Anonymous"
    }), 200

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