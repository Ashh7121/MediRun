from flask import Flask, render_template, request, redirect, url_for, session
from .models import db, Manager
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///medirun.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            user = Manager.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            error = 'Invalid email or password.'
        return render_template('login.html', error=error)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        error = None
        if request.method == 'POST':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            if not all([first_name, last_name, email, password]):
                error = 'All fields are required.'
            elif Manager.query.filter_by(email=email).first():
                error = 'Email already registered.'
            else:
                manager = Manager(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password_hash=generate_password_hash(password),
                )
                db.session.add(manager)
                db.session.commit()
                session['user_id'] = manager.id
                return redirect(url_for('dashboard'))
        return render_template('signup.html', error=error)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    return app
