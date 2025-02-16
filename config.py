import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'trades.db')
    TESTING = False
    SQLALCHEMY_ECHO = False
    TIME_ZONE = 'UTC'
    SECRET_KEY = 'your-secret-key-here'  # Required for CSRF protection


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'trades.db')
    TESTING = False
    TIME_ZONE = 'UTC'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.join(basedir, 'test_trades.db')
    TIME_ZONE = 'UTC'