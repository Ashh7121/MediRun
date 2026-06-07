# models.py
# Database models for the MediRun medical delivery management system.
# Uses Flask-SQLAlchemy with SQLite backend.
# Implements role-based access: 'ceo' (Sophie) and 'driver' roles.

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# USER (authentication & role-based access)
# ---------------------------------------------------------------------------

class User(db.Model):
    """
    Core authentication model for all system users.
    Roles: 'ceo' — full executive access; 'driver' — own deliveries only.
    """
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(64),  nullable=False)
    last_name     = db.Column(db.String(64),  nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  nullable=False)  # 'ceo' | 'driver'
    phone         = db.Column(db.String(20),  nullable=True)
    is_active     = db.Column(db.Boolean,     default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    # If the user is a driver, link to their Driver profile
    driver_profile = db.relationship("DriverProfile", back_populates="user", uselist=False)

    VALID_ROLES = {"ceo", "driver"}

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_ceo(self):
        return self.role == "ceo"

    def is_driver(self):
        return self.role == "driver"

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"


# ---------------------------------------------------------------------------
# DRIVER PROFILE (linked to User with role='driver')
# ---------------------------------------------------------------------------

class DriverProfile(db.Model):
    """
    Extended profile for driver-role users.
    Tracks operational data: license, vehicle, hours.
    """
    __tablename__ = "driver_profiles"

    id                 = db.Column(db.Integer, primary_key=True)
    user_id            = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    license_number     = db.Column(db.String(32), unique=True, nullable=False)
    max_hours_per_day  = db.Column(db.Float,   default=8.0)
    hours_worked_today = db.Column(db.Float,   default=0.0)
    is_available       = db.Column(db.Boolean, default=True)
    van_type           = db.Column(db.String(20), nullable=True)  # 'small' | 'big' | 'refrigerated'

    # Link to User
    user       = db.relationship("User", back_populates="driver_profile")

    # Vehicle assignment
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=True)
    vehicle    = db.relationship("Vehicle", back_populates="current_driver")

    # Deliveries assigned to this driver
    deliveries = db.relationship("Delivery", back_populates="driver")

    @property
    def remaining_hours(self):
        return max(0.0, self.max_hours_per_day - self.hours_worked_today)

    def __repr__(self):
        return (
            f"<DriverProfile id={self.id} user_id={self.user_id} "
            f"license='{self.license_number}' available={self.is_available}>"
        )


# ---------------------------------------------------------------------------
# CLIENT
# ---------------------------------------------------------------------------

class Client(db.Model):
    """
    Delivery recipient: pharmacy, clinic, or healthcare facility.
    """
    __tablename__ = "clients"

    id                     = db.Column(db.Integer, primary_key=True)
    name                   = db.Column(db.String(128), nullable=False)
    organization           = db.Column(db.String(128), nullable=True)
    address                = db.Column(db.String(256), nullable=False)
    city                   = db.Column(db.String(64),  nullable=False)
    is_urban               = db.Column(db.Boolean,     default=True)
    preferred_window_start = db.Column(db.Time, nullable=True)
    preferred_window_end   = db.Column(db.Time, nullable=True)

    deliveries = db.relationship("Delivery", back_populates="client")

    def __repr__(self):
        return f"<Client id={self.id} name='{self.name}' city='{self.city}'>"


# ---------------------------------------------------------------------------
# VEHICLE
# ---------------------------------------------------------------------------

class Vehicle(db.Model):
    """
    Delivery vehicle. size: 'small' (urban) or 'large' (peri-urban).
    temp_flag: True if cold-chain capable.
    """
    __tablename__ = "vehicles"

    id             = db.Column(db.Integer, primary_key=True)
    license_plate  = db.Column(db.String(20), unique=True, nullable=False)
    size           = db.Column(db.String(10), nullable=False)   # 'small' | 'large'
    temp_flag      = db.Column(db.Boolean,    default=False)
    capacity_kg    = db.Column(db.Float,      nullable=False)
    fuel_level     = db.Column(db.Float,      default=100.0)
    is_operational = db.Column(db.Boolean,    default=True)

    current_driver = db.relationship("DriverProfile", back_populates="vehicle", uselist=False)
    deliveries     = db.relationship("Delivery", back_populates="vehicle")

    @property
    def is_urban_suitable(self):
        return self.size == "small"

    def __repr__(self):
        return (
            f"<Vehicle id={self.id} plate='{self.license_plate}' "
            f"size={self.size} temp_flag={self.temp_flag}>"
        )


# ---------------------------------------------------------------------------
# PRODUCT
# ---------------------------------------------------------------------------

class Product(db.Model):
    """
    Medical product for delivery.
    Hard constraint: MAX_VEHICLE_HOURS = 24.
    """
    __tablename__ = "products"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(128), nullable=False)
    amount           = db.Column(db.Float,       nullable=False)
    unit             = db.Column(db.String(20),  default="units")
    weight_kg        = db.Column(db.Float,       nullable=True)
    temp_sensitivity = db.Column(db.Boolean,     default=False)

    MAX_VEHICLE_HOURS = 24

    deliveries = db.relationship("Delivery", back_populates="product")

    def __repr__(self):
        return (
            f"<Product id={self.id} name='{self.name}' "
            f"amount={self.amount} {self.unit} temp_sensitive={self.temp_sensitivity}>"
        )


# ---------------------------------------------------------------------------
# DELIVERY
# ---------------------------------------------------------------------------

class Delivery(db.Model):
    """
    A single delivery task. Status flow: pending → in_progress → delivered | failed.
    Enforces the 24-hour vehicle rule and cold-chain constraint.
    """
    __tablename__ = "deliveries"

    id               = db.Column(db.Integer, primary_key=True)
    start_location   = db.Column(db.String(256), nullable=False)
    destination      = db.Column(db.String(256), nullable=False)
    destination_name = db.Column(db.String(128), nullable=True)
    destination_type = db.Column(db.String(32),  nullable=True)  # 'pharmacy' | 'clinic' | 'hospital'

    # Geographic coordinates for mapping
    dest_lat = db.Column(db.Float, nullable=True)
    dest_lng = db.Column(db.Float, nullable=True)

    # Relationships
    driver_id  = db.Column(db.Integer, db.ForeignKey("driver_profiles.id"), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"),        nullable=True)
    client_id  = db.Column(db.Integer, db.ForeignKey("clients.id"),         nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"),        nullable=True)

    driver  = db.relationship("DriverProfile", back_populates="deliveries")
    vehicle = db.relationship("Vehicle",        back_populates="deliveries")
    client  = db.relationship("Client",         back_populates="deliveries")
    product = db.relationship("Product",        back_populates="deliveries")

    # Scheduling
    scheduled_date    = db.Column(db.Date,     nullable=False, default=datetime.utcnow)
    time_window_start = db.Column(db.Time,     nullable=True)
    time_window_end   = db.Column(db.Time,     nullable=True)
    deadline          = db.Column(db.String(8),nullable=True)  # e.g. "09:00"

    # Priority & temperature
    priority             = db.Column(db.String(20), default="normal")  # 'critical' | 'high' | 'normal'
    temperature_sensitive = db.Column(db.Boolean,   default=False)

    # Lifecycle
    loaded_at    = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Status
    STATUS_OPTIONS = {"pending", "in_progress", "delivered", "failed"}
    status         = db.Column(db.String(20), default="pending", nullable=False)

    route_position = db.Column(db.Integer, nullable=True)

    def validate_cold_chain(self):
        if self.product and self.product.temp_sensitivity:
            if self.vehicle and not self.vehicle.temp_flag:
                raise ValueError(
                    f"Product '{self.product.name}' requires cold-chain but "
                    f"vehicle '{self.vehicle.license_plate}' is not equipped."
                )

    @property
    def hours_in_vehicle(self):
        if self.loaded_at:
            end = self.delivered_at or datetime.utcnow()
            return (end - self.loaded_at).total_seconds() / 3600
        return None

    @property
    def exceeds_24h_limit(self):
        h = self.hours_in_vehicle
        return h is not None and h > Product.MAX_VEHICLE_HOURS

    def __repr__(self):
        return (
            f"<Delivery id={self.id} status='{self.status}' "
            f"driver_id={self.driver_id} priority='{self.priority}'>"
        )
