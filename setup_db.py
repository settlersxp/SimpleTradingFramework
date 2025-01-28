import subprocess
import sys
import logging
from deployment_utils import register_logger, is_windows, get_venv_path

# Setup logging
logger = register_logger('setup_db')

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
    activate_cmd, python_cmd = get_venv_path(logger)
    
    # Construct the database setup command
    db_setup_cmd = '-c "from run import app, db; app.app_context().push(); db.create_all()"'
    
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
