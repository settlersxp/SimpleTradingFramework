import os
import subprocess
import platform
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup_db.log'),
        logging.StreamHandler()
    ]
)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logging.info(result.stdout)
        if result.stderr:
            logging.warning(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        logging.error(f"Output: {e.output}")
        return False

def main():
    # Determine the operating system
    is_windows = platform.system().lower() == "windows"
    
    # Set paths
    base_path = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(base_path, "venv")
    
    # Check if virtual environment exists
    if not os.path.exists(venv_path):
        logging.error(f"Virtual environment not found at {venv_path}")
        sys.exit(1)
    
    # Construct the activation command based on OS
    if is_windows:
        activate_cmd = f"{venv_path}\\Scripts\\activate"
        python_cmd = f"{venv_path}\\Scripts\\python"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
        python_cmd = f"{venv_path}/bin/python"
    
    # Construct the database setup command
    db_setup_cmd = '-c "from app import app, db; app.app_context().push(); db.create_all()"'
    
    # Combine commands
    if is_windows:
        full_command = f"{activate_cmd} && {python_cmd} {db_setup_cmd}"
    else:
        full_command = f"{activate_cmd} && {python_cmd} {db_setup_cmd}"
    
    logging.info("Setting up database...")
    if run_command(full_command):
        logging.info("Database setup completed successfully!")
    else:
        logging.error("Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 