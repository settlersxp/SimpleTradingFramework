from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
import pytz

db = SQLAlchemy()
migrate = Migrate()

# Define timezone for the entire app
APP_TIMEZONE = pytz.timezone('Europe/Berlin')  # UTC+1


class TimezoneAwareModel(db.Model):
    """Base model class that automatically handles timezone conversion"""
    __abstract__ = True

    def get_datetime_in_timezone(self, dt):
        """Convert datetime to app timezone"""
        if dt is None:
            return None

        # If datetime is naive (has no timezone info)
        if dt.tzinfo is None:
            # Assume it's in UTC and make it timezone-aware
            dt = pytz.UTC.localize(dt)

        # Convert to app timezone
        return dt.astimezone(APP_TIMEZONE)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure session cookies work properly
    app.config['SESSION_COOKIE_SECURE'] = config_class.DEBUG is False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.prop_firms import bp as prop_firms_bp
    from app.routes.trades import bp as trades_bp
    from app.routes.trades_association import bp as trades_association_bp
    from app.routes.trade_pairs import bp as trade_pairs_bp
    from app.routes.auth import auth_bp
    from app.routes.user_prop_firms import user_prop_firms_bp

    app.register_blueprint(prop_firms_bp, url_prefix='/prop_firms')
    app.register_blueprint(trades_bp, url_prefix='/trades')
    app.register_blueprint(trades_association_bp, url_prefix='/trades_association')
    app.register_blueprint(trade_pairs_bp, url_prefix='/trade_pairs')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_prop_firms_bp, url_prefix='/api/user_prop_firms')

    return app 