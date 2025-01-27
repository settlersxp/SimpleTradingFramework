from app import create_app
from config import DevelopmentConfig, Config
from app import db
from flask_migrate import Migrate
from flask import jsonify

app = create_app()
app.config.from_object(DevelopmentConfig)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3200)
