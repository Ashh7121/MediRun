"""
seed_db.py
Initializes the MediRun SQLite database and seeds it with:
  - 1 CEO account (Sophie)
  - 5 Driver accounts
  - Sample deliveries, vehicles, products, clients

Run once before starting the application:
    python seed_db.py
"""

import os
import sys

# Ensure the package is importable from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from delivery_app.app import create_app
from delivery_app.models import db, User, DriverProfile, Vehicle, Product, Client, Delivery
from datetime import date


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("🗑️  Dropped and recreated all tables.")

        # ── CEO ──────────────────────────────────────────────────────────────
        sophie = User(
            first_name="Sophie",
            last_name="Martin",
            email="sophie@medirun.fr",
            role="ceo",
        )
        sophie.set_password("MediRun2024!")
        db.session.add(sophie)

        # ── Vehicles ─────────────────────────────────────────────────────────
        vehicles = [
            Vehicle(license_plate="AB-123-CD", size="small", temp_flag=False, capacity_kg=200.0),
            Vehicle(license_plate="EF-456-GH", size="large", temp_flag=False, capacity_kg=800.0),
            Vehicle(license_plate="IJ-789-KL", size="small", temp_flag=False, capacity_kg=200.0),
            Vehicle(license_plate="MN-012-OP", size="large", temp_flag=True,  capacity_kg=700.0),
            Vehicle(license_plate="QR-345-ST", size="large", temp_flag=False, capacity_kg=900.0),
        ]
        for v in vehicles:
            db.session.add(v)
        db.session.flush()  # get IDs

        # ── Driver users ──────────────────────────────────────────────────────
        driver_data = [
            ("Marc",   "Dubois",   "marc@medirun.fr",   "Driver2024!",  "DL-001", "small",        vehicles[0]),
            ("Luc",    "Bernard",  "luc@medirun.fr",    "Driver2024!",  "DL-002", "big",           vehicles[1]),
            ("Ahmed",  "Hassan",   "ahmed@medirun.fr",  "Driver2024!",  "DL-003", "small",        vehicles[2]),
            ("Sophie", "Durand",   "sdurand@medirun.fr","Driver2024!",  "DL-004", "refrigerated", vehicles[3]),
            ("Jean",   "Lefevre",  "jean@medirun.fr",   "Driver2024!",  "DL-005", "big",           vehicles[4]),
        ]

        driver_users = []
        for first, last, email, pwd, lic, van_type, veh in driver_data:
            u = User(first_name=first, last_name=last, email=email, role="driver")
            u.set_password(pwd)
            db.session.add(u)
            db.session.flush()
            profile = DriverProfile(
                user_id=u.id,
                license_number=lic,
                van_type=van_type,
                vehicle_id=veh.id,
            )
            db.session.add(profile)
            driver_users.append((u, profile))

        db.session.flush()

        # ── Products ─────────────────────────────────────────────────────────
        products = [
            Product(name="Paracetamol 500mg", amount=100, unit="boxes",  weight_kg=5.0,  temp_sensitivity=False),
            Product(name="Insulin Glargine",  amount=20,  unit="vials",  weight_kg=1.0,  temp_sensitivity=True),
            Product(name="Amoxicillin 250mg", amount=50,  unit="boxes",  weight_kg=3.0,  temp_sensitivity=False),
            Product(name="Epinephrine 1mg",   amount=10,  unit="vials",  weight_kg=0.5,  temp_sensitivity=True),
            Product(name="Bandages Kit",      amount=30,  unit="packs",  weight_kg=8.0,  temp_sensitivity=False),
        ]
        for p in products:
            db.session.add(p)
        db.session.flush()

        # ── Clients ───────────────────────────────────────────────────────────
        clients = [
            Client(name="Hôpital Saint-Jean",      organization="Saint-Jean",       address="12 rue des Lilas",           city="Paris",           is_urban=True),
            Client(name="Clinique Pasteur",         organization="Clinique Pasteur", address="18 boulevard Pasteur",       city="Paris",           is_urban=True),
            Client(name="Pharmacie Centrale",       organization=None,               address="3 avenue Gambetta",          city="Paris",           is_urban=True),
            Client(name="Clinique Ivry",            organization="Clinique Ivry",    address="56 avenue du Dr Ingard",     city="Ivry-sur-Seine",  is_urban=False),
            Client(name="Pharmacie Montreuil",      organization=None,               address="67 avenue Jean Lolive",      city="Montreuil",       is_urban=False),
        ]
        for c in clients:
            db.session.add(c)
        db.session.flush()

        # ── Sample deliveries (assigned to real driver profiles) ──────────────
        warehouse = "18 rue Jules Vanzuppe, 94200 Ivry-sur-Seine"

        # driver_profiles: marc=0, luc=1, ahmed=2, sophie_d=3, jean=4
        sample_deliveries = [
            Delivery(
                start_location=warehouse,
                destination=clients[0].address,
                destination_name=clients[0].name,
                destination_type="hospital",
                dest_lat=48.8238, dest_lng=2.3575,
                driver_id=driver_users[0][1].id,
                vehicle_id=vehicles[0].id,
                client_id=clients[0].id,
                product_id=products[0].id,
                scheduled_date=date.today(),
                deadline="09:00",
                priority="critical",
                temperature_sensitive=False,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination=clients[1].address,
                destination_name=clients[1].name,
                destination_type="clinic",
                dest_lat=48.8348, dest_lng=2.3148,
                driver_id=driver_users[3][1].id,
                vehicle_id=vehicles[3].id,
                client_id=clients[1].id,
                product_id=products[1].id,
                scheduled_date=date.today(),
                deadline="11:00",
                priority="high",
                temperature_sensitive=True,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination=clients[2].address,
                destination_name=clients[2].name,
                destination_type="pharmacy",
                dest_lat=48.8707, dest_lng=2.3968,
                driver_id=driver_users[2][1].id,
                vehicle_id=vehicles[2].id,
                client_id=clients[2].id,
                product_id=products[2].id,
                scheduled_date=date.today(),
                deadline="14:00",
                priority="normal",
                temperature_sensitive=False,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination=clients[3].address,
                destination_name=clients[3].name,
                destination_type="clinic",
                dest_lat=48.7210, dest_lng=2.3634,
                driver_id=driver_users[1][1].id,
                vehicle_id=vehicles[1].id,
                client_id=clients[3].id,
                product_id=products[3].id,
                scheduled_date=date.today(),
                deadline="10:00",
                priority="high",
                temperature_sensitive=True,
                status="in_progress",
            ),
            Delivery(
                start_location=warehouse,
                destination=clients[4].address,
                destination_name=clients[4].name,
                destination_type="pharmacy",
                dest_lat=48.8618, dest_lng=2.4412,
                driver_id=driver_users[4][1].id,
                vehicle_id=vehicles[4].id,
                client_id=clients[4].id,
                product_id=products[4].id,
                scheduled_date=date.today(),
                deadline="16:00",
                priority="normal",
                temperature_sensitive=False,
                status="pending",
            ),
            # A few more to bulk up the dashboard
            Delivery(
                start_location=warehouse,
                destination="78 rue Oberkampf, 75011 Paris",
                destination_name="Pharmacie Oberkampf",
                destination_type="pharmacy",
                dest_lat=48.8660, dest_lng=2.3779,
                driver_id=driver_users[0][1].id,
                vehicle_id=vehicles[0].id,
                product_id=products[0].id,
                scheduled_date=date.today(),
                deadline="11:30",
                priority="normal",
                temperature_sensitive=False,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination="91 rue Amelot, 75011 Paris",
                destination_name="Clinique Urgence 11",
                destination_type="clinic",
                dest_lat=48.8594, dest_lng=2.3721,
                driver_id=driver_users[3][1].id,
                vehicle_id=vehicles[3].id,
                product_id=products[1].id,
                scheduled_date=date.today(),
                deadline="09:45",
                priority="critical",
                temperature_sensitive=True,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination="85 rue Mouffetard, 75005 Paris",
                destination_name="Pharmacie Gobelins",
                destination_type="pharmacy",
                dest_lat=48.8387, dest_lng=2.3515,
                driver_id=driver_users[2][1].id,
                vehicle_id=vehicles[2].id,
                product_id=products[2].id,
                scheduled_date=date.today(),
                deadline="10:00",
                priority="normal",
                temperature_sensitive=False,
                status="delivered",
            ),
            Delivery(
                start_location=warehouse,
                destination="34 rue Sèvres, 75006 Paris",
                destination_name="Clinique Sèvres",
                destination_type="clinic",
                dest_lat=48.8478, dest_lng=2.3290,
                driver_id=driver_users[3][1].id,
                vehicle_id=vehicles[3].id,
                product_id=products[3].id,
                scheduled_date=date.today(),
                deadline="13:30",
                priority="high",
                temperature_sensitive=True,
                status="pending",
            ),
            Delivery(
                start_location=warehouse,
                destination="42 rue Victor Basch, 94120 Fontenay-sous-Bois",
                destination_name="Pharmacie Fontenay",
                destination_type="pharmacy",
                dest_lat=48.8476, dest_lng=2.4801,
                driver_id=driver_users[1][1].id,
                vehicle_id=vehicles[1].id,
                product_id=products[4].id,
                scheduled_date=date.today(),
                deadline="17:00",
                priority="normal",
                temperature_sensitive=False,
                status="pending",
            ),
        ]

        for d in sample_deliveries:
            db.session.add(d)

        db.session.commit()
        print("✅ Database seeded successfully!")
        print()
        print("=== AUTHORIZED ACCOUNTS ===")
        print()
        print("CEO:")
        print(f"  Email:    sophie@medirun.fr")
        print(f"  Password: MediRun2024!")
        print()
        print("Drivers (all share password: Driver2024!):")
        for first, last, email, *_ in driver_data:
            print(f"  {first} {last:<12} — {email}")
        print()
        print(f"Deliveries seeded: {len(sample_deliveries)}")


if __name__ == "__main__":
    seed()
