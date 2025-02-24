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

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.prop_firms import bp as prop_firms_bp
    from app.routes.trades import bp as trades_bp
    from app.routes.trades_association import bp as trades_association_bp
    from app.routes.trade_pairs import bp as trade_pairs_bp

    app.register_blueprint(prop_firms_bp, url_prefix='/prop_firms')
    app.register_blueprint(trades_bp, url_prefix='/trades')
    app.register_blueprint(trades_association_bp, url_prefix='/trades_association')
    app.register_blueprint(trade_pairs_bp, url_prefix='/trade_pairs')

    return app 