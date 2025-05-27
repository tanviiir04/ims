from flask import Flask, request, jsonify, session, send_from_directory, redirect
from models    import db, User, Incident

from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to access this page'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def main():
    return send_from_directory('static', 'login.html')

@app.route('/index.html')
def index():
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful', 'user': user.name}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name} for u in users])

@app.route('/api/incidents', methods=['GET'])
@login_required
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([{
        'id': i.id,
        'title': i.title,
        'description': i.description,
        'priority': i.priority,
        'category': i.category,
        'assigned_to': i.assigned_to,
        'status': i.status,
        'createdAt': i.createdAt.isoformat() if i.createdAt else None,
        'resolved_at': i.resolved_at.isoformat() if i.resolved_at else None,
        'sla_deadline': i.sla_deadline.isoformat() if i.sla_deadline else None
    } for i in incidents])

@app.route('/api/incidents', methods=['POST'])
@login_required
def create_incident():
    data = request.json
    sla_hours = 4
    incident = Incident(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'IT'),
        assigned_to=data.get('assigned_to'),
        status='open',
        createdAt=datetime.utcnow(),
        sla_deadline=datetime.utcnow() + timedelta(hours=sla_hours)
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify({'message': 'Incident created', 'id': incident.id}), 201

@app.route('/api/incidents/<int:incident_id>/resolve', methods=['POST'])
@login_required
def resolve_incident(incident_id):
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'message': 'Incident not found'}), 404
    incident.status = 'resolved'
    incident.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Incident resolved'}), 200

@app.route('/api/incidents/sla-metrics', methods=['GET'])
@login_required
def sla_metrics():
    incidents = Incident.query.filter(Incident.status != 'resolved').all()
    now = datetime.utcnow()
    metrics = {
        'breached': 0,
        'at_risk': 0,
        'on_track': 0
    }
    for incident in incidents:
        if not incident.sla_deadline:
            continue
        if now > incident.sla_deadline:
            metrics['breached'] += 1
        elif (incident.sla_deadline - now).total_seconds() < 3600:
            metrics['at_risk'] += 1
        else:
            metrics['on_track'] += 1
    return jsonify(metrics)

if __name__ == '__main__':
    print("🟡 Starting app...")
    with app.app_context():
        print("🧹 Dropping and creating fresh database...")
        db.drop_all()
        db.create_all()
        
        default_users = [
            {'name': 'Sam', 'position': 'Manager', 'username': 'Sam10', 'password': 'Sam01'},
            {'name': 'Pip', 'position': 'HoD Sales', 'username': 'Pip21', 'password': 'Pip12'},
            {'name': 'Jen', 'position': 'HoD Designing', 'username': 'Jen31', 'password': 'Jen13'},
            {'name': 'Tom', 'position': 'HoD Marketing', 'username': 'Tom41', 'password': 'Tom14'},
            {'name': 'Ben', 'position': 'HoD Accounts', 'username': 'Ben51', 'password': 'Ben15'}
        ]

        for u in default_users:
            print(f"➕ Creating user: {u['username']}")
            user = User(name=u['name'], position=u['position'], username=u['username'], password=u['password'])
            db.session.add(user)
        
        db.session.commit()
        print("✅ Database and users ready.")

    app.run(debug=False)
