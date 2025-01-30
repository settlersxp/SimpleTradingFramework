from app import create_app, db
from config import DevelopmentConfig
from flask import jsonify
import os
import signal
from flask_migrate import upgrade
import logging

PID = os.getpid()


class FlaskApp:
    def __init__(self):
        self.app = create_app()
        self.app.config.from_object(DevelopmentConfig)
        
        # Initialize database with migrations
        try:
            with self.app.app_context():
                # Check if migrations directory exists
                if os.path.exists('migrations'):
                    # Run all pending migrations
                    upgrade()
                else:
                    # If no migrations exist, create tables directly
                    db.create_all()
                    logging.warning("No migrations found. Created tables directly.")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            pass

        # Register routes
        self.register_routes()
    
    def register_routes(self):
        @self.app.route('/', methods=['GET'])
        def hello():
            return jsonify({"message": "Hello, World!"})

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy"})
            
        @self.app.route('/shutdown', methods=['GET'])
        def shutdown():
            # this mimics a CTRL+C hit by sending SIGINT
            # it ends the app run, but not the main thread
            pid = os.getpid()
            assert pid == PID
            os.kill(pid, signal.SIGINT)
            return "OK", 200
    
    def run(self):
        self.app.run(host='0.0.0.0', port=3200, use_reloader=False, threaded=True)


if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.run()
