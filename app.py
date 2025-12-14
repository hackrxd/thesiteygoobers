import os
import random
import json
from flask import Flask, request, abort, send_file, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename

# --- Flask app setup ---
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
maintenence = False

# --- Utility functions ---
def block_ip(ip):
    with open('blocked_ips.txt', 'a') as f:
        f.write(f"{ip}\n")

def load_blocked_ips():
    if not os.path.exists('blocked_ips.txt'):
        return []
    with open('blocked_ips.txt', 'r') as f:
        return [line.strip() for line in f]

def load_new_ui_addrs():
    if not os.path.exists('newui.txt'):
        return []
    with open('newui.txt', 'r') as f:
        return [line.strip() for line in f]

# --- Error handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

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
        return flask.redirect('/error')

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
@app.route('/', methods=['GET'])
def home():
    if newUI:
        return send_from_directory('uiupdate', 'index.html')
    return send_file('index.html')

@app.route('/main.css', methods=['GET'])
def styling():
    return send_file('main.css', mimetype='text/css')

@app.route('/events/', methods=['GET'])
def events():
    return send_from_directory('events', 'index.html')

@app.route('/events/annual/')
def annevent():
    return send_from_directory('events/annual', 'index.html')

@app.route('/events/annual/<filename>', methods=['GET'])
def serve_annual(filename):
    file = f"{filename}.html"
    return send_from_directory('events/annual', file)

@app.route('/events/anonymous/', methods=['GET'])
def anonymous_event():
    return send_file('anonymousanomaly.html')

@app.route('/members/', methods=['GET'])
def members():
    return send_from_directory('members', 'index.html')

@app.route('/files/<path:filepath>')
def serve_files(filepath):
    full_path = os.path.join("files", filepath)
    if not os.path.isfile(full_path):
        abort(404)
    return send_from_directory('files', filepath)

@app.route('/uploads/<filename>')
def show_upload(filename):
    return send_from_directory('uploads', filename)

@app.route('/api/webtextdata', methods=['GET'])
def get_quotes():
    if not os.path.exists('webtextdata.json'):
        return jsonify([])
    try:
        with open('webtextdata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return jsonify([])
    return jsonify(data)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "File not found"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    safe_name = secure_filename(file.filename)
    filename = f"{random.randint(1000000, 100000000)}-{random.randint(1000000, 100000000)}-{safe_name}".lower()
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return jsonify({
        "originalName": file.filename,
        "storedName": filename,
        "fileUrl": f'/uploads/{filename}',
        "uploader": "Anonymous"
    }), 200

# --- Systemd/Gunicorn pattern: do NOT run app.run() ---
# The app will be run by Gunicorn:
#   gunicorn -w 3 -b 127.0.0.1:8000 your_module_name:app
