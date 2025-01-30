from flask_migrate import Migrate
from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Import models so that Flask-Migrate can detect them
        from app.models import PropFirm, Trade
        db.create_all()
