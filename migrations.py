from flask_migrate import Migrate
from run import flask_app
from app import db

migrate = Migrate(flask_app, db)

if __name__ == '__main__':
    with flask_app.app_context():
        # Import models so that Flask-Migrate can detect them
        from app.models import PropFirm, Trade, TradePairs
        db.create_all()