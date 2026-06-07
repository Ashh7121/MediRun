"""
app.py — MediRun Flask application factory.

Authentication & Authorization:
- Login is required for all routes beyond /login.
- CEO (role='ceo'): full dashboard, KPIs, all deliveries, all drivers.
- Driver (role='driver'): own delivery list only.
- Public sign-up is disabled. Only pre-seeded accounts can log in.

Database:
- SQLite backend via SQLAlchemy (configured in config.py / env var).
- All data comes from the database; no dummy/mock data structures are used.

VRP assignment:
- The AssignDeliveriesService still runs on the live DB delivery list,
  represented as plain dicts so the algorithm needs zero changes.
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, abort
)
from .models import db, User, DriverProfile, Delivery, Vehicle, Product, Client
from .config import Config
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime
import os
import sys

# ── Allow the services package to be imported regardless of cwd ──────────────
_SERVICES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'services')
)
if _SERVICES_DIR not in sys.path:
    sys.path.insert(0, _SERVICES_DIR)

from assign_driver import AssignDeliveriesService


# ── Auth decorators ───────────────────────────────────────────────────────────

def login_required(f):
    """Redirect to login if the user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def ceo_required(f):
    """Abort 403 if the logged-in user is not the CEO."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_ceo():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Return the User object for the current session, or None."""
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None


# ── Data helpers ──────────────────────────────────────────────────────────────

def _delivery_to_dict(delivery: Delivery) -> dict:
    """Convert a Delivery ORM object to the dict format expected by the VRP service."""
    return {
        "id":                   delivery.id,
        "destination_type":     delivery.destination_type or "pharmacy",
        "location": {
            "name":    delivery.destination_name or delivery.destination,
            "address": delivery.destination,
            "lat":     delivery.dest_lat or 48.8566,
            "lng":     delivery.dest_lng or 2.3522,
        },
        "temperature_sensitive": delivery.temperature_sensitive,
        "priority":              delivery.priority or "normal",
        "deadline":              delivery.deadline or "18:00",
        "status":                delivery.status,
        "driver_id":             delivery.driver_id,
        "driver_name":           (
            delivery.driver.user.full_name() if delivery.driver and delivery.driver.user else "Unassigned"
        ),
        "van_type":              (delivery.driver.van_type if delivery.driver else "unknown"),
    }


def _driver_to_dict(profile: DriverProfile) -> dict:
    """Convert a DriverProfile ORM object to the dict format expected by the VRP service."""
    return {
        "id":         profile.id,
        "name":       profile.user.full_name() if profile.user else f"Driver {profile.id}",
        "van_type":   profile.van_type or "small",
        "is_available": profile.is_available,
    }


def build_assignment_data():
    """
    Pull live data from the database, run the VRP assignment algorithm,
    and return a structured dict for the dashboard and API.
    """
    from collections import defaultdict

    # Fetch all today's deliveries and available driver profiles
    all_deliveries = Delivery.query.filter_by(scheduled_date=datetime.utcnow().date()).all()
    if not all_deliveries:
        all_deliveries = Delivery.query.all()  # fallback: show all if no today's

    all_profiles = DriverProfile.query.join(User).filter(User.is_active == True).all()

    delivery_dicts = [_delivery_to_dict(d) for d in all_deliveries]
    driver_dicts   = [_driver_to_dict(p) for p in all_profiles]

    warehouse = {
        "name":    "MediRun Warehouse",
        "address": "18 rue Jules Vanzuppe, 94200 Ivry-sur-Seine",
        "lat":     48.7165,
        "lng":     2.3812,
    }

    # Run the VRP algorithm
    service     = AssignDeliveriesService(delivery_dicts, driver_dicts, warehouse)
    assignments = service.assignments   # {driver_id (profile.id): [delivery_id, ...]}

    # Index helpers
    driver_map   = {d['id']: d for d in driver_dicts}
    delivery_map = {d['id']: d for d in delivery_dicts}

    # Enrich deliveries with driver info
    enriched = []
    for driver_id, delivery_ids in assignments.items():
        driver = driver_map.get(driver_id, {})
        for did in delivery_ids:
            d = delivery_map.get(did)
            if d:
                enriched.append({**d, 'driver_id': driver_id, 'driver_name': driver.get('name', 'Unknown')})

    priority_order = {'critical': 0, 'high': 1, 'normal': 2}
    enriched.sort(key=lambda d: (priority_order.get(d['priority'], 9), d['deadline']))

    # Driver summaries
    driver_counts   = defaultdict(int)
    for driver_id, ids in assignments.items():
        driver_counts[driver_id] = len(ids)

    driver_summaries = []
    for profile in all_profiles:
        pid   = profile.id
        d_ids = assignments.get(pid, [])
        driver_deliveries = [
            {**delivery_map[eid], 'driver_id': pid,
             'driver_name': driver_map.get(pid, {}).get('name', '')}
            for eid in d_ids if eid in delivery_map
        ]
        driver_summaries.append({
            **driver_map.get(pid, {}),
            'delivery_count': len(d_ids),
            'deliveries':     driver_deliveries,
        })

    stats = {
        'total_deliveries': len(delivery_dicts),
        'active_drivers':   sum(1 for pid in driver_map if driver_counts.get(pid, 0) > 0),
        'total_drivers':    len(driver_dicts),
        'critical_count':   sum(1 for d in delivery_dicts if d['priority'] == 'critical'),
        'temp_sensitive':   sum(1 for d in delivery_dicts if d['temperature_sensitive']),
        'delivered_count':  sum(1 for d in delivery_dicts if d['status'] == 'delivered'),
        'pending_count':    sum(1 for d in delivery_dicts if d['status'] == 'pending'),
    }

    return {
        'deliveries': enriched,
        'drivers':    driver_summaries,
        'stats':      stats,
        'warehouse':  warehouse,
    }


def build_driver_data(profile: DriverProfile) -> dict:
    """Build the delivery data for a specific driver (for the driver portal)."""
    deliveries = Delivery.query.filter_by(driver_id=profile.id).all()
    delivery_dicts = [_delivery_to_dict(d) for d in deliveries]

    priority_order = {'critical': 0, 'high': 1, 'normal': 2}
    delivery_dicts.sort(key=lambda d: (priority_order.get(d['priority'], 9), d['deadline']))

    warehouse = {
        "name":    "MediRun Warehouse",
        "address": "18 rue Jules Vanzuppe, 94200 Ivry-sur-Seine",
        "lat":     48.7165,
        "lng":     2.3812,
    }

    return {
        'driver': {
            'id':       profile.id,
            'name':     profile.user.full_name(),
            'van_type': profile.van_type,
            'is_available': profile.is_available,
            'delivery_count': len(delivery_dicts),
            'deliveries': delivery_dicts,
        },
        'warehouse': warehouse,
        'stats': {
            'total':     len(delivery_dicts),
            'pending':   sum(1 for d in delivery_dicts if d['status'] == 'pending'),
            'delivered': sum(1 for d in delivery_dicts if d['status'] == 'delivered'),
            'critical':  sum(1 for d in delivery_dicts if d['priority'] == 'critical'),
        }
    }


# ── Application factory ───────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ── 403 handler ───────────────────────────────────────────────────────────

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    # ── Root ──────────────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        user = get_current_user()
        if user:
            if user.is_ceo():
                return redirect(url_for('dashboard'))
            elif user.is_driver():
                return redirect(url_for('driver_portal'))
        return redirect(url_for('login'))

    # ── Login ─────────────────────────────────────────────────────────────────

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Already authenticated — redirect appropriately
        if 'user_id' in session:
            return redirect(url_for('index'))

        error = None
        if request.method == 'POST':
            email    = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = User.query.filter_by(email=email, is_active=True).first()
            if user and user.check_password(password):
                session['user_id']   = user.id
                session['user_role'] = user.role
                session['user_name'] = user.full_name()
                if user.is_ceo():
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('driver_portal'))
            error = 'Invalid email or password.'

        return render_template('login.html', error=error)

    # ── Logout ────────────────────────────────────────────────────────────────

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ── CEO: Executive Dashboard ──────────────────────────────────────────────

    @app.route('/dashboard')
    @ceo_required
    def dashboard():
        data = build_assignment_data()
        now  = datetime.now().strftime('%A, %d %B')
        user = get_current_user()
        return render_template('dashboard.html', data=data, now=now, user=user)

    # ── CEO: Driver detail page ───────────────────────────────────────────────

    @app.route('/driver/<int:driver_id>')
    @ceo_required
    def driver_page(driver_id):
        data   = build_assignment_data()
        driver = next((d for d in data['drivers'] if d['id'] == driver_id), None)
        if driver is None:
            return redirect(url_for('dashboard'))
        return render_template('driver.html', driver=driver, warehouse=data['warehouse'])

    # ── Driver: own portal ────────────────────────────────────────────────────

    @app.route('/my-deliveries')
    @login_required
    def driver_portal():
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        # CEO should not be hitting this route — send them to dashboard
        if user.is_ceo():
            return redirect(url_for('dashboard'))

        profile = DriverProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            return render_template('driver_portal.html', data=None, user=user)

        data = build_driver_data(profile)
        now  = datetime.now().strftime('%A, %d %B')
        return render_template('driver_portal.html', data=data, user=user, now=now)

    # ── Driver: update delivery status ────────────────────────────────────────

    @app.route('/delivery/<int:delivery_id>/status', methods=['POST'])
    @login_required
    def update_delivery_status(delivery_id):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        delivery = Delivery.query.get_or_404(delivery_id)

        # Drivers can only update their own deliveries
        if user.is_driver():
            profile = DriverProfile.query.filter_by(user_id=user.id).first()
            if not profile or delivery.driver_id != profile.id:
                return jsonify({'error': 'Forbidden'}), 403

        new_status = request.form.get('status') or request.json.get('status', '')
        if new_status not in Delivery.STATUS_OPTIONS:
            return jsonify({'error': f'Invalid status: {new_status}'}), 400

        delivery.status = new_status
        if new_status == 'in_progress' and not delivery.loaded_at:
            delivery.loaded_at = datetime.utcnow()
        if new_status == 'delivered' and not delivery.delivered_at:
            delivery.delivered_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'success': True, 'status': delivery.status})

    # ── CEO REST API ──────────────────────────────────────────────────────────

    @app.route('/api/assignments')
    @ceo_required
    def api_assignments():
        return jsonify(build_assignment_data())

    @app.route('/api/driver/<int:driver_id>/deliveries')
    @login_required
    def api_driver_deliveries(driver_id):
        """
        Drivers can only fetch their own deliveries.
        CEO can fetch any driver's deliveries.
        """
        user = get_current_user()
        if user.is_driver():
            profile = DriverProfile.query.filter_by(user_id=user.id).first()
            if not profile or profile.id != driver_id:
                abort(403)

        profile = DriverProfile.query.get_or_404(driver_id)
        data    = build_driver_data(profile)
        return jsonify(data)

    return app
