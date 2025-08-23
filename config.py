import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "tradesv2.db")
    TESTING = False
    SQLALCHEMY_ECHO = False
    TIME_ZONE = "UTC"

    # Generate a strong secret key if not already available
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    SESSION_USE_SIGNER = True  # Sign the session cookie for added security


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "tradesv2.db")
    TESTING = False
    TIME_ZONE = "UTC"
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test_tradesv2.db")
    TIME_ZONE = "UTC"
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in testing
