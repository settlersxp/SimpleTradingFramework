from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    # migrate.init_app(app, db)

    # Register blueprints
    from app.routes.prop_firms import bp as prop_firms_bp
    from app.routes.trades import bp as trades_bp
    from app.routes.trades_association import bp as trades_association_bp

    app.register_blueprint(prop_firms_bp, url_prefix='/prop_firms')
    app.register_blueprint(trades_bp, url_prefix='/trades')
    app.register_blueprint(trades_association_bp, url_prefix='/trades_association')

    return app 