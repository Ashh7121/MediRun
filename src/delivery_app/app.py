from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from .models import db, Manager
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import sys

# ── allow the services package to be imported regardless of cwd ──────────────
_SERVICES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'services')
)
if _SERVICES_DIR not in sys.path:
    sys.path.insert(0, _SERVICES_DIR)

from assign_driver import AssignDeliveriesService
from test_dummy_data import DRIVERS, DELIVERIES, WAREHOUSE


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def build_assignment_data():
    """
    Run the assignment algorithm and return a structured dict
    consumed by the dashboard and the API endpoint.
    """
    service = AssignDeliveriesService(DELIVERIES, DRIVERS, WAREHOUSE)
    assignments = service.assignments          # {driver_id: [delivery_id, ...]}

    # Index helpers
    driver_map   = {d['id']: d for d in DRIVERS}
    delivery_map = {d['id']: d for d in DELIVERIES}

    # ── Build flat enriched delivery list ────────────────────────────────────
    enriched_deliveries = []
    driver_delivery_counts = {d['id']: 0 for d in DRIVERS}

    for driver_id, delivery_ids in assignments.items():
        driver = driver_map.get(driver_id, {})
        driver_delivery_counts[driver_id] = len(delivery_ids)
        for did in delivery_ids:
            d = delivery_map.get(did)
            if d:
                enriched_deliveries.append({
                    **d,
                    'driver_id':   driver_id,
                    'driver_name': driver.get('name', 'Unknown'),
                    'van_type':    driver.get('van_type', 'unknown'),
                })

    # Sort: critical first, then high, then normal; within group sort by deadline
    priority_order = {'critical': 0, 'high': 1, 'normal': 2}
    enriched_deliveries.sort(
        key=lambda d: (priority_order.get(d['priority'], 9), d['deadline'])
    )

    # ── Build driver summary list ─────────────────────────────────────────────
    driver_summaries = []
    for driver in DRIVERS:
        did = driver['id']
        d_ids = assignments.get(did, [])
        driver_deliveries = [
            {**delivery_map[eid], 'driver_id': did,
             'driver_name': driver['name'], 'van_type': driver['van_type']}
            for eid in d_ids if eid in delivery_map
        ]
        driver_summaries.append({
            **driver,
            'delivery_count': len(d_ids),
            'deliveries':     driver_deliveries,
        })

    # ── KPI stats ─────────────────────────────────────────────────────────────
    stats = {
        'total_deliveries': len(DELIVERIES),
        'active_drivers':   len([d for d in DRIVERS if driver_delivery_counts.get(d['id'], 0) > 0]),
        'total_drivers':    len(DRIVERS),
        'critical_count':   sum(1 for d in DELIVERIES if d['priority'] == 'critical'),
        'temp_sensitive':   sum(1 for d in DELIVERIES if d['temperature_sensitive']),
    }

    return {
        'deliveries':  enriched_deliveries,
        'drivers':     driver_summaries,
        'stats':       stats,
        'warehouse':   WAREHOUSE,
    }


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///medirun.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ── Auth routes ───────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            email    = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            user     = Manager.query.filter_by(email=email).first()
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
            last_name  = request.form.get('last_name',  '').strip()
            email      = request.form.get('email',      '').strip()
            password   = request.form.get('password',   '')
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

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ── Dashboard ─────────────────────────────────────────────────────────────

    @app.route('/dashboard')
    @login_required
    def dashboard():
        data = build_assignment_data()
        now  = datetime.now().strftime('%A, %d %B')
        return render_template('dashboard.html', data=data, now=now)

    # ── Driver detail page ────────────────────────────────────────────────────

    @app.route('/driver/<int:driver_id>')
    @login_required
    def driver_page(driver_id):
        data = build_assignment_data()

        driver = next(
            (d for d in data['drivers'] if d['id'] == driver_id), None
        )
        if driver is None:
            return redirect(url_for('dashboard'))

        return render_template(
            'driver.html',
            driver=driver,
            warehouse=data['warehouse'],
        )

    # ── REST API ──────────────────────────────────────────────────────────────

    @app.route('/api/assignments')
    @login_required
    def api_assignments():
        """
        JSON endpoint consumed by the dashboard's Refresh button.
        Returns the same structure as build_assignment_data().
        """
        return jsonify(build_assignment_data())

    return app
