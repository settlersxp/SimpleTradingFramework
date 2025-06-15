from app import create_app, db
from config import DevelopmentConfig
from flask import jsonify, request, g, render_template
from flask_migrate import Migrate
from app.models.prop_firm import PropFirm
import os
import signal
import logging
import time
from datetime import datetime
import json

# Setup logging with more explicit configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a specific logger for requests
request_logger = logging.getLogger("request_logger")
request_logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicates
if request_logger.handlers:
    request_logger.handlers.clear()

# Create file handler with absolute path and immediate flush
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.log")


class SafeFileHandler(logging.FileHandler):
    def emit(self, record):
        """Safely emit a record."""
        try:
            msg = self.format(record)
            with open(self.baseFilename, "a", encoding=self.encoding) as f:
                f.write(msg + self.terminator)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            self.handleError(record)


# Replace the FileHandler creation with:
fh = SafeFileHandler(log_file_path, mode="a", encoding="utf-8", delay=False)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)

# Add handler to logger
request_logger.addHandler(fh)

# Add stream handler for console output during debugging
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
request_logger.addHandler(ch)

# Ensure logger propagates
request_logger.propagate = False

# Test the logger immediately
request_logger.info("Logger initialization test")
fh.flush()


class FlaskApp:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FlaskApp, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.app = create_app()
        self.app.config.from_object(DevelopmentConfig)

        # Initialize migrations
        self.migrate = Migrate(self.app, db)

        # Register middleware before routes
        self.register_middleware()

        # Register routes
        self.register_routes()

        self._initialized = True

    def register_middleware(self):
        @self.app.before_request
        def before_request():
            """Log the request details"""
            g.start_time = time.time()

            # Get request body
            request_body = request.get_data(as_text=True)
            if request_body:
                try:
                    request_body = json.loads(request_body)
                except json.JSONDecodeError:
                    request_body = request_body

            log_data = {
                "type": "request",
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "path": request.path,
                "headers": dict(request.headers),
                "query_params": dict(request.args),
                "body": request_body,
                "remote_addr": request.remote_addr,
            }

            # Log and flush immediately only if the user agent is "Go-http-client"
            if request.headers.get(
                "User-Agent"
            ) and "Go-http-client" in request.headers.get("User-Agent"):
                request_logger.info(json.dumps(log_data, indent=2))

            for handler in request_logger.handlers:
                handler.flush()

        @self.app.after_request
        def after_request(response):
            """Log the response details"""
            # Calculate request duration
            duration = time.time() - g.start_time

            # Get response body
            response_body = response.get_data(as_text=True)
            if response_body:
                try:
                    response_body = json.loads(response_body)
                except json.JSONDecodeError:
                    response_body = response_body

            log_data = {
                "type": "response",
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "duration": f"{duration:.4f}s",
            }

            # Log and flush immediately only if the user agent is "Go-http-client"
            if response.headers.get(
                "User-Agent"
            ) and "Go-http-client" in response.headers.get("User-Agent"):
                request_logger.info(json.dumps(log_data, indent=2))

            for handler in request_logger.handlers:
                handler.flush()

            return response

    def register_routes(self):
        @self.app.route("/", methods=["GET"])
        def hello():
            return render_template("index.html")

        @self.app.route("/open_positions", methods=["POST"], strict_slashes=False)
        def open_positions():
            from app.routes.trades import handle_trade_with_parameters
            from app.routes.signals import save_signal

            saved_signal = save_signal(request.get_data(as_text=True))
            return handle_trade_with_parameters(
                request.get_data(as_text=True),
                saved_signal,
            )

        @self.app.route("/api/trades", methods=["POST"], strict_slashes=False)
        def api_trades():
            # Used in order to create a trade from the API using an already saved signal
            from app.routes.trades import handle_trade_with_parameters
            from app.routes.signals import Signal

            signal = Signal.from_mt_string(request.get_data(as_text=True))
            return handle_trade_with_parameters(signal)

        @self.app.route("/trades", methods=["POST"], strict_slashes=False)
        def trades():
            # Used in order to create a trade from the API using a new signal
            from app.routes.trades import handle_trade_with_parameters
            from app.routes.signals import save_signal

            saved_signal = save_signal(request.get_data(as_text=True))
            return handle_trade_with_parameters(saved_signal)

        @self.app.route("/receiveMessage", methods=["POST"], strict_slashes=False)
        def receive_message():
            from app.routes.trades import handle_trade_with_parameters
            from app.routes.signals import save_signal

            saved_signal = save_signal(request.get_data(as_text=True))
            return handle_trade_with_parameters(saved_signal)

        @self.app.route("/health", methods=["GET"])
        def health():
            prop_firms = PropFirm.query.all()

            # Prepare health status
            health_status = {"status": "healthy", "prop_firms": []}

            for firm in prop_firms:
                # Check if the trading instance is connected
                is_connected = (
                    firm.trading is not None and firm.trading.is_connected()
                )  # Assuming is_connected() is a method in your TradingInterface

                health_status["prop_firms"].append(
                    {
                        "id": firm.id,
                        "name": firm.name,
                        "is_active": firm.is_active,
                        "connected": is_connected,
                    }
                )
            return jsonify(health_status)

        @self.app.route("/shutdown", methods=["GET"])
        def shutdown():
            os.kill(os.getpid(), signal.SIGINT)
            return "OK", 200

    def run(self):
        self.app.run(host="0.0.0.0", port=3100, use_reloader=False, threaded=True)


# Create a single Flask application instance
flask_app = FlaskApp().app
flask_app.url_map.strict_slashes = False


if __name__ == "__main__":
    # Use the same instance
    FlaskApp().run()
