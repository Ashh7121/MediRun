# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure instance/ directory exists relative to the project root
_INSTANCE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'instance'))
os.makedirs(_INSTANCE_DIR, exist_ok=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(_INSTANCE_DIR, 'medirun.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'medirun-dev-secret-key-change-in-production')
