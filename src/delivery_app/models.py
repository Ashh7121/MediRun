# database schemas (drivers, tasks)
# This defines what your data looks like. 
# It tells the app: "A Driver must have a Name and an ID," 
# and "A Destination must have an Address and a Status."
# database schemas (drivers, tasks)
# This defines what your data looks like. 
# It tells the app: "A Driver must have a Name and an ID," 
# and "A Destination must have an Address and a Status."

# models.py
# Database models for the medical delivery management system.
# Uses Flask-SQLAlchemy for ORM mapping.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# PERSON hierarchy
# ---------------------------------------------------------------------------

class Person(db.Model):
    """
    Abstract base for all human actors in the system.
    Uses SQLAlchemy's joined-table inheritance so Manager, Driver, and Client
    each get their own table while sharing common identity columns here.
    """
    __tablename__ = "persons"

    id           = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(64),  nullable=False)
    last_name    = db.Column(db.String(64),  nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    phone        = db.Column(db.String(20),  nullable=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    password_hash = db.Column(db.String(256), nullable=True)

    # Discriminator column — SQLAlchemy uses this to know which subclass to load
    person_type  = db.Column(db.String(20),  nullable=False)

    __mapper_args__ = {
        "polymorphic_on":      person_type,
        "polymorphic_identity": "person",   # base identity (never instantiated directly)
    }

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Person id={self.id} name='{self.full_name()}' type='{self.person_type}'>"


class Manager(Person):
    """
    Plans and assigns deliveries. Has access to the dashboard and
    can create/modify delivery tasks and driver assignments.
    """
    __tablename__ = "managers"

    id         = db.Column(db.Integer, db.ForeignKey("persons.id"), primary_key=True)
    department = db.Column(db.String(64), nullable=True)   # e.g. "Operations", "Logistics"

    __mapper_args__ = {"polymorphic_identity": "manager"}

    def __repr__(self):
        return f"<Manager id={self.id} name='{self.full_name()}'>"


class Driver(Person):
    """
    Executes deliveries. Bound by working-hour and rest-time regulations.
    Assigned to a specific vehicle for a given day.
    """
    __tablename__ = "drivers"

    id                    = db.Column(db.Integer, db.ForeignKey("persons.id"), primary_key=True)
    license_number        = db.Column(db.String(32),  unique=True, nullable=False)
    max_hours_per_day     = db.Column(db.Float,       default=8.0)   # legal daily limit (hours)
    hours_worked_today    = db.Column(db.Float,       default=0.0)   # resets each day
    is_available          = db.Column(db.Boolean,     default=True)  # False if on leave/rest

    # A driver is assigned to one vehicle at a time (nullable = not yet assigned)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=True)
    vehicle    = db.relationship("Vehicle", back_populates="current_driver")

    # All deliveries ever assigned to this driver
    deliveries = db.relationship("Delivery", back_populates="driver")

    __mapper_args__ = {"polymorphic_identity": "driver"}

    @property
    def remaining_hours(self):
        """How many working hours the driver still has today."""
        return max(0.0, self.max_hours_per_day - self.hours_worked_today)

    def __repr__(self):
        return (
            f"<Driver id={self.id} name='{self.full_name()}' "
            f"available={self.is_available} hours_left={self.remaining_hours:.1f}h>"
        )


class Client(Person):
    """
    Recipient of deliveries — typically a pharmacy, clinic, or healthcare facility.
    Stores the delivery address and any time-window preference.
    """
    __tablename__ = "clients"

    id               = db.Column(db.Integer, db.ForeignKey("persons.id"), primary_key=True)
    organization     = db.Column(db.String(128), nullable=True)   # e.g. "Clinique Saint-Louis"
    address          = db.Column(db.String(256), nullable=False)
    city             = db.Column(db.String(64),  nullable=False)
    is_urban         = db.Column(db.Boolean,     default=True)    # urban vs peri-urban location

    # Preferred delivery window (optional — soft constraint)
    preferred_window_start = db.Column(db.Time, nullable=True)
    preferred_window_end   = db.Column(db.Time, nullable=True)

    # Deliveries addressed to this client
    deliveries = db.relationship("Delivery", back_populates="client")

    __mapper_args__ = {"polymorphic_identity": "client"}

    def __repr__(self):
        return f"<Client id={self.id} org='{self.organization}' city='{self.city}'>"


# ---------------------------------------------------------------------------
# VEHICLE
# ---------------------------------------------------------------------------

class Vehicle(db.Model):
    """
    Represents a delivery vehicle in the heterogeneous fleet.

    size      — 'small' (agile, urban) or 'large' (high-capacity, peri-urban).
    temp_flag — True if the vehicle has a refrigeration/temperature-controlled
                compartment, required for temp-sensitive medical products.
    """
    __tablename__ = "vehicles"

    id              = db.Column(db.Integer, primary_key=True)
    license_plate   = db.Column(db.String(20), unique=True, nullable=False)
    size            = db.Column(db.String(10),  nullable=False)   # 'small' | 'large'
    temp_flag       = db.Column(db.Boolean,     default=False)    # cold-chain capable?
    capacity_kg     = db.Column(db.Float,       nullable=False)   # max load in kilograms
    fuel_level      = db.Column(db.Float,       default=100.0)    # percentage 0–100
    is_operational  = db.Column(db.Boolean,     default=True)

    # The driver currently assigned to this vehicle (one-to-one for a given day)
    current_driver = db.relationship("Driver", back_populates="vehicle", uselist=False)

    # All deliveries performed with this vehicle
    deliveries = db.relationship("Delivery", back_populates="vehicle")

    VALID_SIZES = {"small", "large"}

    def __init__(self, **kwargs):
        if "size" in kwargs and kwargs["size"] not in self.VALID_SIZES:
            raise ValueError(f"Vehicle size must be one of {self.VALID_SIZES}")
        super().__init__(**kwargs)

    @property
    def is_urban_suitable(self):
        """Small vehicles are preferred for dense urban areas."""
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
    A medical product to be delivered.

    amount           — quantity (units, boxes, etc.) in this shipment.
    temp_sensitivity — True if the product requires temperature-controlled
                       transport (e.g. vaccines, insulin). Triggers a check
                       that the assigned vehicle has temp_flag=True.
    """
    __tablename__ = "products"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(128), nullable=False)
    amount           = db.Column(db.Float,       nullable=False)   # quantity in shipment
    unit             = db.Column(db.String(20),  default="units")  # e.g. 'boxes', 'vials'
    weight_kg        = db.Column(db.Float,       nullable=True)    # total weight of shipment
    temp_sensitivity = db.Column(db.Boolean,     default=False)    # requires cold chain?

    # Hard constraint: no product can stay in a vehicle more than 24 hours
    MAX_VEHICLE_HOURS = 24

    # All deliveries carrying this product
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
    A single delivery task: one product shipment, one driver, one vehicle,
    from a start location to a client's destination.

    Key business rules encoded here:
    - A temp-sensitive product requires a temp-flagged vehicle (validated on creation).
    - The 24-hour vehicle limit is tracked via loaded_at / delivered_at.
    - Status flows: pending → in_progress → delivered | failed.
    """
    __tablename__ = "deliveries"

    id               = db.Column(db.Integer, primary_key=True)
    start_location   = db.Column(db.String(256), nullable=False)   # warehouse / depot address
    destination      = db.Column(db.String(256), nullable=False)   # client delivery address

    # Core relationships
    driver_id  = db.Column(db.Integer, db.ForeignKey("drivers.id"),   nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"),  nullable=True)
    client_id  = db.Column(db.Integer, db.ForeignKey("clients.id"),   nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"),  nullable=False)

    driver  = db.relationship("Driver",  back_populates="deliveries")
    vehicle = db.relationship("Vehicle", back_populates="deliveries")
    client  = db.relationship("Client",  back_populates="deliveries")
    product = db.relationship("Product", back_populates="deliveries")

    # Scheduling
    scheduled_date   = db.Column(db.Date,     nullable=False, default=datetime.utcnow)
    time_window_start = db.Column(db.Time,    nullable=True)   # soft constraint
    time_window_end   = db.Column(db.Time,    nullable=True)   # soft constraint

    # Lifecycle timestamps — used to enforce the 24-hour rule
    loaded_at        = db.Column(db.DateTime, nullable=True)   # when product entered vehicle
    delivered_at     = db.Column(db.DateTime, nullable=True)   # when product left vehicle
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Status
    STATUS_OPTIONS = {"pending", "in_progress", "delivered", "failed"}
    status           = db.Column(db.String(20), default="pending", nullable=False)

    # Sequence position within a driver's daily route (for ordering)
    route_position   = db.Column(db.Integer, nullable=True)

    def validate_cold_chain(self):
        """
        Hard constraint: a temperature-sensitive product must be assigned
        to a vehicle with cold-chain capability (temp_flag=True).
        Raises ValueError if the constraint is violated.
        """
        if self.product and self.product.temp_sensitivity:
            if self.vehicle and not self.vehicle.temp_flag:
                raise ValueError(
                    f"Product '{self.product.name}' is temperature-sensitive but "
                    f"vehicle '{self.vehicle.license_plate}' has no cold-chain capability."
                )

    @property
    def hours_in_vehicle(self):
        """Returns how long the product has been in the vehicle (hours), or None."""
        if self.loaded_at:
            end = self.delivered_at or datetime.utcnow()
            delta = end - self.loaded_at
            return delta.total_seconds() / 3600
        return None

    @property
    def exceeds_24h_limit(self):
        """True if the product has been in the vehicle longer than 24 hours."""
        h = self.hours_in_vehicle
        return h is not None and h > Product.MAX_VEHICLE_HOURS

    def __repr__(self):
        return (
            f"<Delivery id={self.id} status='{self.status}' "
            f"driver_id={self.driver_id} product_id={self.product_id}>"
        )