import threading
import time
import requests
from deployment_utils import (
    register_logger,
    get_venv_path,
    run_command_as_subprocess_with_stream,
    kill_python_process,
)

CHECK_INTERVAL = 5  # seconds
WATCH_HASH_FILE = "last_folder_hash.txt"
SAVE_HASH_FILE = "saved_folder_hash.txt"

logger = register_logger('monitor_and_run')


def save_hash(folder_hash):
    """Save the current folder hash"""
    with open(SAVE_HASH_FILE, 'w') as f:
        f.write(folder_hash)


def get_saved_hash(hash_file_path):
    """Get the last saved folder hash"""
    try:
        with open(hash_file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.flask_app = None
        self._stop_event = threading.Event()
    
    def run(self):
        try:
            # Get venv paths
            activate_cmd, python_cmd = get_venv_path(logger)
            
            # Combine commands to run Flask app
            full_command = f"{activate_cmd} && {python_cmd} run.py"
            
            logger.info("Starting Flask server...")
            run_command_as_subprocess_with_stream(full_command, logger)
        except Exception as e:
            logger.error(f"Error running Flask app: {e}")
    
    def stop(self):
        """Shutdown the Flask app"""
        try:
            requests.get('http://localhost:3200/shutdown')
            self._stop_event.set()
        except Exception as e:
            logger.error(f"Error stopping Flask app: {e}")
            # Force process kill if graceful shutdown fails
            kill_python_process(logger, 'run.py')
            self._stop_event.set()


def monitor_and_restart():
    """Monitor for changes and restart Flask app when needed"""
    flask_thread = None
    
    if flask_thread is None:
        flask_thread = FlaskThread()
        flask_thread.daemon = True
        flask_thread.start()
        logger.info("Started new Flask thread")

    while True:
        try:
            folder_hash = get_saved_hash(WATCH_HASH_FILE)
            existing_hash = get_saved_hash(SAVE_HASH_FILE)
            
            if folder_hash != existing_hash:
                logger.info("Changes detected in the application")
                
                # Stop existing Flask thread if running
                if flask_thread and flask_thread.is_alive():
                    flask_thread.stop()
                    flask_thread.join(timeout=5)
                    logger.info("Stopped existing Flask thread")
                
                # Save new hash
                save_hash(folder_hash)
                
                # Start new Flask thread
                flask_thread = FlaskThread()
                flask_thread.daemon = True
                flask_thread.start()
                logger.info("Started new Flask thread")

            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Stopping monitor...")
            if flask_thread and flask_thread.is_alive():
                flask_thread.stop()
                flask_thread.join(timeout=5)
                logger.info("Stopped Flask thread")
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    logger.info("Starting application monitor")
    monitor_and_restart()
