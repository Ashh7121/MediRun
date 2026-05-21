# database URLs/secret keys
# Contains secret settings, like your database password 
# or "Secret Keys" that keep your login system secure.

# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # This points SQLite to create 'medical_delivery.db' inside src\delivery_app
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'medical_delivery.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-mvp-safety'