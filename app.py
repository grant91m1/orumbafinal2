from flask import Flask, send_from_directory, request, jsonify, session, redirect, url_for, render_template
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime, timezone
import bcrypt
from functools import wraps

from app.db import db
from app.people import PEOPLE
from app.storage import MAX_FILE_SIZE, storage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

secret_key = os.environ.get('SECRET_KEY')
if os.environ.get('FLASK_ENV') == 'production':
    required_env = ('SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY')
    missing_env = [name for name in required_env if not os.environ.get(name)]
    if missing_env:
        raise RuntimeError('Missing required production environment variables: ' + ', '.join(missing_env))
    if os.environ.get('USE_CLOUD_STORAGE', '').lower() != 'true':
        raise RuntimeError('USE_CLOUD_STORAGE=true is required in production')

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static',
    template_folder=os.path.join(BASE_DIR, 'app', 'templates'),
)
app.secret_key = secret_key or secrets.token_hex(24)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE + 1024 * 1024

# HTTPS is used in production, while local development runs over HTTP.
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'lax')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'

# Named officials, available to every template as `people`
app.jinja_env.globals['people'] = PEOPLE

# CSRF Protection
csrf = CSRFProtect(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URI', 'memory://'),
    default_limits=["200 per day", "50 per hour"]
)

# Code the council gives to authorised writers so they can create an account
WRITER_INVITE_CODE = os.environ.get('WRITER_INVITE_CODE', '').strip()

posts = []
users = []
events = []
albums = []

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder, 'images'), 'favicon-32.png', mimetype='image/png')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

def hash_password(password):
    """Hash password using bcrypt for secure storage."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify password against bcrypt hash. Supports legacy SHA256 for migration."""
    # Try bcrypt first (new format)
    try:
        if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
            return True
    except Exception:
        pass

    # Fallback to SHA256 for legacy passwords (old format)
    legacy_hash = hashlib.sha256(password.encode()).hexdigest()
    return hashed == legacy_hash

def load_posts():
    global posts
    loaded = db.load_posts()
    for p in loaded:
        if 'user_id' not in p:
            p['user_id'] = None
        if 'category' not in p:
            p['category'] = 'general'
        if 'status' not in p:
            p['status'] = 'published' if p.get('author') else 'draft'
        if 'image' not in p:
            p['image'] = ''
    posts = loaded

def load_users():
    global users
    loaded = db.load_users()
    next_user_id = 1
    for user in loaded:
        if 'id' not in user:
            user['id'] = next_user_id
            next_user_id += 1
        if 'role' not in user:
            user['role'] = 'writer'
        if 'name' not in user:
            user['name'] = user['username']
        if 'email' not in user:
            user['email'] = ''
        if 'avatar' not in user:
            user['avatar'] = ''
    users = loaded

def load_events():
    global events
    events = db.load_events()

def load_albums():
    global albums
    loaded = db.load_albums()
    for alb in loaded:
        if 'user_id' not in alb:
            alb['user_id'] = None
    albums = loaded

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('serve_login'))
        current_user = next((u for u in users if u['username'] == session['username']), None)
        if not current_user:
            session.pop('username', None)
            return redirect(url_for('serve_login'))
        if 'id' not in current_user:
            current_user['id'] = 1
        if 'role' not in current_user:
            current_user['role'] = 'writer'
        session['user_id'] = current_user['id']
        session['role'] = current_user['role']
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    username = session.get('username')
    return next((u for u in users if u['username'] == username), None) if username else None

# Profile routes
@app.route('/profile')
@app.route('/profile/<section>')
@login_required
def profile(section='dashboard'):
    return render_template('profile/profile.html', section=section)

@app.route('/api/profile/stats', methods=['GET'])
@login_required
def api_profile_stats():
    user_id = session.get('user_id')
    post_count = len([p for p in posts if p.get('user_id') == user_id])
    album_count = len([a for a in albums if a.get('user_id') == user_id])
    event_count = len([e for e in events if e.get('user_id') == user_id])
    return jsonify({
        'status': 'success',
        'stats': {'posts': post_count, 'albums': album_count, 'events': event_count}
    })

@app.route('/api/profile/posts', methods=['GET'])
@login_required
def api_profile_posts():
    user_id = session.get('user_id')
    user_posts = [p for p in posts if p.get('user_id') == user_id]
    return jsonify({'status': 'success', 'posts': user_posts})

@app.route('/api/profile/posts', methods=['POST'])
@login_required
def api_create_post():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid post is required'}), 400
    title = str(data.get('title', '')).strip()
    content = str(data.get('content', '')).strip()
    status = data.get('status', 'draft')
    if not title or len(title) > 200 or not content or len(content) > 50000:
        return jsonify({'status': 'error', 'message': 'Post title and content are required and must fit the allowed lengths'}), 400
    if status not in ('draft', 'published'):
        return jsonify({'status': 'error', 'message': 'Post status must be draft or published'}), 400
    user_id = session.get('user_id')
    max_id = max([p.get('id', 0) for p in posts], default=0)
    new_post = {
        'id': max_id + 1,
        'user_id': user_id,
        'title': title,
        'content': content,
        'category': data.get('category', 'general'),
        'image': data.get('image', ''),
        'status': status,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    db.save_post(new_post)
    posts.append(new_post)
    return jsonify({'status': 'success', 'post': new_post})

@app.route('/api/profile/posts/<int:post_id>', methods=['PUT'])
@login_required
def api_update_post(post_id):
    user_id = session.get('user_id')
    post = next((p for p in posts if p['id'] == post_id and p.get('user_id') == user_id), None)
    if not post:
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid post update is required'}), 400
    updates = {key: data[key] for key in ('title', 'content', 'category', 'image', 'status') if key in data}
    db.update_post(post_id, updates)
    post.update(updates)
    return jsonify({'status': 'success', 'post': post})

@app.route('/api/profile/posts/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    user_id = session.get('user_id')
    global posts
    if not any(p.get('id') == post_id and p.get('user_id') == user_id for p in posts):
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404
    db.delete_post(post_id, user_id)
    posts = [p for p in posts if not (p.get('id') == post_id and p.get('user_id') == user_id)]
    return jsonify({'status': 'success'})

@app.route('/api/profile/albums', methods=['GET'])
@login_required
def api_profile_albums():
    user_id = session.get('user_id')
    user_albums = [a for a in albums if a.get('user_id') == user_id]
    return jsonify({'status': 'success', 'albums': user_albums})

@app.route('/api/profile/albums', methods=['POST'])
@login_required
def api_create_album():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid album is required'}), 400
    title = str(data.get('title', '')).strip()
    album_posts = data.get('posts', [])
    if (
        not title
        or len(title) > 160
        or not isinstance(album_posts, list)
        or not 1 <= len(album_posts) <= 100
        or any(
            not isinstance(post, dict)
            or not isinstance(post.get('image_url'), str)
            or not post['image_url'].startswith(('/static/uploads/', 'https://'))
            or not isinstance(post.get('caption', ''), str)
            or len(post.get('caption', '')) > 500
            for post in album_posts
        )
    ):
        return jsonify({'status': 'error', 'message': 'Album title and image list are invalid'}), 400
    user_id = session.get('user_id')
    max_id = max([a.get('id', 0) for a in albums], default=0)
    new_album = {
        'id': max_id + 1,
        'user_id': user_id,
        'title': title,
        'posts': album_posts
    }
    db.save_album(new_album)
    albums.append(new_album)
    return jsonify({'status': 'success', 'album': new_album})

@app.route('/api/profile/albums/<int:album_id>', methods=['DELETE'])
@login_required
def api_delete_album(album_id):
    user_id = session.get('user_id')
    global albums
    if not any(a.get('id') == album_id and a.get('user_id') == user_id for a in albums):
        return jsonify({'status': 'error', 'message': 'Album not found'}), 404
    db.delete_album(album_id, user_id)
    albums = [a for a in albums if not (a.get('id') == album_id and a.get('user_id') == user_id)]
    return jsonify({'status': 'success'})

@app.route('/api/profile/events', methods=['GET'])
@login_required
def api_profile_events():
    user_id = session.get('user_id')
    user_events = [e for e in events if e.get('user_id') == user_id]
    return jsonify({'status': 'success', 'events': user_events})

@app.route('/api/profile/events', methods=['POST'])
@login_required
def api_create_event():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid event is required'}), 400
    title = str(data.get('title', '')).strip()
    date = str(data.get('date', '')).strip()
    location = str(data.get('location', '')).strip()
    content = str(data.get('content', '')).strip()
    image = str(data.get('image', '')).strip()
    try:
        datetime.fromisoformat(date.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'A valid event date is required'}), 400
    if not title or len(title) > 160 or not location or len(location) > 200:
        return jsonify({'status': 'error', 'message': 'Event title and location are required'}), 400
    if len(content) > 20000 or len(image) > 2048:
        return jsonify({'status': 'error', 'message': 'Event details exceed the allowed length'}), 400
    if image and not image.startswith(('/static/uploads/', 'https://')):
        return jsonify({'status': 'error', 'message': 'Event image must be uploaded to the site'}), 400
    status = data.get('status', 'draft')
    if status not in ('draft', 'published'):
        return jsonify({'status': 'error', 'message': 'Event status must be draft or published'}), 400
    user_id = session.get('user_id')
    max_id = max([e.get('id', 0) for e in events], default=0)
    new_event = {
        'id': max_id + 1,
        'user_id': user_id,
        'title': title,
        'date': date,
        'location': location,
        'content': content,
        'image': image,
        'status': status,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    db.save_event(new_event)
    events.append(new_event)
    return jsonify({'status': 'success', 'event': new_event})

@app.route('/api/profile/events/<int:event_id>', methods=['DELETE'])
@login_required
def api_delete_event(event_id):
    user_id = session.get('user_id')
    global events
    if not any(e.get('id') == event_id and e.get('user_id') == user_id for e in events):
        return jsonify({'status': 'error', 'message': 'Event not found'}), 404
    db.delete_event(event_id, user_id)
    events = [e for e in events if not (e.get('id') == event_id and e.get('user_id') == user_id)]
    return jsonify({'status': 'success'})

@app.route('/api/upload/image', methods=['POST'])
@login_required
def api_upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    user_id = session.get('user_id')
    subfolder = f'user_{user_id}'

    success, url, error = storage.save_file(file, file.filename, subfolder)

    if success:
        return jsonify({'status': 'success', 'url': url})
    else:
        return jsonify({'status': 'error', 'message': error or 'Upload failed'}), 400

@app.route('/api/profile/settings', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid profile update is required'}), 400
    username = session['username']
    user = next(u for u in users if u['username'] == username)
    allowed = ['name', 'email', 'avatar']
    if any(not isinstance(data[key], str) for key in allowed if key in data):
        return jsonify({'status': 'error', 'message': 'Profile fields must be text'}), 400
    updates = {key: data[key].strip() for key in allowed if key in data}
    if 'name' in updates and (len(updates['name']) < 2 or len(updates['name']) > 120):
        return jsonify({'status': 'error', 'message': 'Name must be between 2 and 120 characters'}), 400
    if 'email' in updates and updates['email'] and (
        len(updates['email']) > 254 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', updates['email'])
    ):
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address'}), 400
    db.update_user(username, updates)
    for key in allowed:
        if key in updates:
            user[key] = updates[key]
    return jsonify({'status': 'success'})

# Load initial data
load_users()
load_posts()
load_albums()
load_events()

@app.route('/')
def serve_home():
    return render_template('home.html')

# The writer area is reached by its own address; it is not linked from the public menu.
@app.route('/writers/login', methods=['GET'])
def serve_login():
    return render_template('login.html')

@app.route('/writers/register', methods=['GET'])
def serve_register():
    return render_template(
        'register.html',
        registration_open=writer_registration_open(),
        invite_required=bool(WRITER_INVITE_CODE),
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('serve_home'))

def writer_registration_open():
    """Writer accounts are created with the council's invite code.

    With no code configured, registration is closed in production and left
    open in local development.
    """
    return bool(WRITER_INVITE_CODE) or os.environ.get('FLASK_ENV') != 'production'

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per hour")
def api_register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid registration request is required'}), 400
    if not writer_registration_open():
        return jsonify({'status': 'error', 'message': 'Writer registration is closed. Contact the council ICT unit for an account.'}), 403
    if WRITER_INVITE_CODE:
        invite_code = data.get('invite_code', '')
        if not isinstance(invite_code, str) or not hmac.compare_digest(invite_code.strip().encode(), WRITER_INVITE_CODE.encode()):
            return jsonify({'status': 'error', 'message': 'The invite code is not valid'}), 403
    username = data.get('username', '')
    password = data.get('password', '')
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({'status': 'error', 'message': 'Username and password must be text'}), 400
    username = username.strip()
    password = password.strip()

    # Input validation
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    if len(username) < 3 or len(username) > 50:
        return jsonify({'status': 'error', 'message': 'Username must be 3-50 characters'}), 400
    if len(password) < 8:
        return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters'}), 400

    if any(u['username'] == username for u in users):
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 400

    hashed_pw = hash_password(password)
    new_user = {
        'username': username,
        'password': hashed_pw,
        'id': max([u.get('id', 0) for u in users], default=0) + 1,
        'role': 'writer',
        'name': username,
        'email': '',
        'avatar': ''
    }
    try:
        db.save_user(new_user)
    except Exception:
        app.logger.exception('Unable to save registration')
        return jsonify({'status': 'error', 'message': 'Unable to create account right now. Please try again later.'}), 500

    users.append(new_user)
    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid login request is required'}), 400
    username = data.get('username', '')
    password = data.get('password', '')
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({'status': 'error', 'message': 'Username and password must be text'}), 400
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    user = next((u for u in users if u['username'] == username), None)
    if user and verify_password(password, user['password']):
        session['username'] = username
        return jsonify({'status': 'success', 'message': 'Logged in successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})

@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per hour")
def api_contact():
    if request.is_json:
        data = request.get_json(silent=True)
    else:
        data = request.form.to_dict()

    if not isinstance(data, dict):
        return jsonify({'status': 'error', 'message': 'A valid contact message is required'}), 400

    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    message = str(data.get('message', '')).strip()

    if not all([name, email, message]):
        return jsonify({'status': 'error', 'message': 'Name, email, and message are required'}), 400
    if len(name) < 2 or len(name) > 120:
        return jsonify({'status': 'error', 'message': 'Name must be between 2 and 120 characters'}), 400
    if len(email) > 254 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address'}), 400
    if len(message) < 10 or len(message) > 5000:
        return jsonify({'status': 'error', 'message': 'Message must be between 10 and 5000 characters'}), 400

    db.save_contact_message({'name': name, 'email': email, 'message': message})
    return jsonify({'status': 'success', 'message': 'Thank you for your message. We will respond within 48 hours.'})

@app.route('/api/check-auth', methods=['GET'])
def api_check_auth():
    if 'username' in session:
        user = get_current_user()
        return jsonify({
            'status': 'success',
            'authenticated': True,
            'username': session['username'],
            'name': user.get('name', session['username']) if user else session['username'],
            'email': user.get('email', '') if user else ''
        })
    else:
        return jsonify({'status': 'success', 'authenticated': False})

@app.route('/create-post')
@login_required
def serve_create_post():
    return render_template('create_post.html')

@app.route('/create-album')
@login_required
def serve_create_album():
    return render_template('create_album.html')

@app.route('/create-event')
@login_required
def serve_create_event():
    return render_template('create_event.html')

@app.route('/api/public/posts', methods=['GET'])
def api_public_get_posts():
    public_posts = [p for p in posts if p.get('status') == 'published']
    return jsonify({'status': 'success', 'posts': public_posts})

@app.route('/api/public/events', methods=['GET'])
def api_public_get_events():
    public_events = [e for e in events if e.get('status') == 'published']
    return jsonify({'status': 'success', 'events': public_events})

@app.route('/api/public/post/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    post = next((p for p in posts if p.get('id') == post_id and p.get('status') == 'published'), None)
    if post:
        return jsonify({
            'status': 'success',
            'post': {
                'id': post.get('id'),
                'title': post.get('title', 'Untitled'),
                'content': post.get('content'),
                'username': post.get('author'),
                'published_at': post.get('published_at') or post.get('created_at')
            }
        })
    return jsonify({'status': 'error', 'message': 'Post not found'}), 404

@app.route('/api/public/albums', methods=['GET'])
def api_public_get_albums():
    return jsonify({'status': 'success', 'albums': albums})

@app.route('/about')
def serve_about():
    return render_template('about.html')

@app.route('/services')
def serve_services():
    return render_template('services.html')

@app.route('/members')
def serve_members():
    return render_template('members.html')

@app.route('/government')
def serve_government():
    return render_template('government.html')

@app.route('/government/administration')
def serve_administration():
    return render_template('government/administration.html')

@app.route('/government/management-team')
def serve_management_team():
    return render_template('government/management-team.html')

@app.route('/chairman-leadership')
def serve_chairman():
    return redirect(url_for('serve_management_team'))

@app.route('/procedure-by-laws')
def serve_procedure():
    return render_template('government.html')

@app.route('/map-explore')
def serve_map():
    return render_template('map-explore.html')

@app.route('/contact')
def serve_contact():
    return render_template('contact.html')

@app.route('/about/history')
def serve_history():
    return render_template('about/history.html')

@app.route('/about/landmarks-culture')
def serve_culture():
    return render_template('about/landmarks-culture.html')

@app.route('/about/people')
def serve_people():
    return render_template('about/people.html')

@app.route('/news-announcements')
def serve_news():
    return render_template('news-announcements.html')

@app.route('/gallery')
def serve_gallery():
    return render_template('gallery.html')

@app.route('/newsroom')
def serve_newsroom():
    return render_template('newsroom.html')

@app.route('/upcoming-events')
def serve_upcoming_events():
    return render_template('upcoming-events.html')

@app.route('/post/<int:post_id>')
def serve_post(post_id):
    return render_template('post.html')

@app.route('/departments')
def serve_departments():
    return render_template('departments.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
