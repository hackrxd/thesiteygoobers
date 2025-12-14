import os
import random
import json
from flask import request
import subprocess
from flask import Flask, request, abort, send_from_directory, jsonify, redirect

# --- Base directories ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
BLOCKED_IPS_FILE = os.path.join(BASE_DIR, 'blocked_ips.txt')
NEW_UI_FILE = os.path.join(BASE_DIR, 'newui.txt')
WEBTEXT_FILE = os.path.join(BASE_DIR, 'webtextdata.json')

# --- Flask app setup ---
app = Flask(__name__, static_folder=PUBLIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
maintenence = False

@app.route('/deploy', methods=['POST'])
def webhook_deploy():
    # Optional: validate GitHub secret
    subprocess.call(['/home/hackr/deploy.sh'])
    return 'Deploy triggered', 200


# --- Utility functions ---
def block_ip(ip):
    with open(BLOCKED_IPS_FILE, 'a') as f:
        f.write(f"{ip}\n")

def load_blocked_ips():
    if not os.path.exists(BLOCKED_IPS_FILE):
        return []
    with open(BLOCKED_IPS_FILE, 'r') as f:
        return [line.strip() for line in f]

def load_new_ui_addrs():
    if not os.path.exists(NEW_UI_FILE):
        return []
    with open(NEW_UI_FILE, 'r') as f:
        return [line.strip() for line in f]

# --- Request pre-processing ---
@app.before_request
def before_request():
    global newUI
    newUI = False

    blocked_ips = load_blocked_ips()
    newUIaddrs = load_new_ui_addrs()
    full_url = request.full_path

    # Maintenance check
    if (maintenence and request.path not in ['/error', '/main.css']
        and request.remote_addr not in ["127.0.0.1"]):
        return redirect('/error')

    # Blocked IP check
    if request.remote_addr in blocked_ips and request.path != "/main.css":
        abort(403)

    # Malicious pattern check
    malicious_patterns = [
        "wget%20", "%20sh", "|", ";", "nc%20", "rm%20-rf", 
        "etc/passwd", "mstshash=Administr", "\\x02\\x01\\x00",
        "/_next/", "\\x00"
    ]
    if any(pattern in full_url for pattern in malicious_patterns):
        block_ip(request.remote_addr)
        abort(400)

    # New UI flag
    if request.remote_addr in newUIaddrs:
        newUI = True

# --- Routes ---

# Root route
@app.route('/', methods=['GET'])
def home():
    if newUI:
        ui_file = os.path.join(BASE_DIR, 'uiupdate', 'index.html')
        if os.path.exists(ui_file):
            return send_from_directory(os.path.join(BASE_DIR, 'uiupdate'), 'index.html')
    index_file = os.path.join(PUBLIC_DIR, 'index.html')
    if os.path.exists(index_file):
        return send_from_directory(PUBLIC_DIR, 'index.html')
    abort(404)

# Serve static files (CSS, JS, members, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    file_path = os.path.join(PUBLIC_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(PUBLIC_DIR, filename)
    # Also serve uploads
    upload_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(upload_path):
        return send_from_directory(UPLOAD_DIR, filename)
    abort(404)

@app.route('/api/updatewebtext', methods=['POST'])
def updateQuote():
    # Create a dictionary for the quote and author
    data = request.get_json()

    message = data.get('message')
    author = data.get('author')
    
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
    return jsonify({"status": "success", "message": "Quote saved successfully."}), 200

# API endpoint for JSON data
@app.route('/api/webtextdata', methods=['GET'])
def get_quotes():
    if not os.path.exists(WEBTEXT_FILE):
        return jsonify([])
    try:
        with open(WEBTEXT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return jsonify([])
    return jsonify(data)

# File uploads
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "File not found"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    safe_name = secure_filename(file.filename)
    filename = f"{random.randint(1000000, 100000000)}-{random.randint(1000000,100000000)}-{safe_name}".lower()
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)
    return jsonify({
        "originalName": file.filename,
        "storedName": filename,
        "fileUrl": f'/uploads/{filename}',
        "uploader": "Anonymous"
    }), 200

# Error routes (optional custom pages)
@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory(PUBLIC_DIR, '404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return send_from_directory(PUBLIC_DIR, '403.html'), 403

@app.errorhandler(400)
def bad_request(e):
    return send_from_directory(PUBLIC_DIR, '400.html'), 400

@app.errorhandler(500)
def server_error(e):
    return send_from_directory(PUBLIC_DIR, '500.html'), 500

# --- Gunicorn will run this app; do NOT use app.run() ---
