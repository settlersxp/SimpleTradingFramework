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
        logging.FileHandler('run_server.log'),
        logging.StreamHandler()
    ]
)

def run_command(command):
    try:
        # Use subprocess.Popen to keep the server running
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Stream the output in real-time
        while True:
            output = process.stdout.readline()
            if output:
                logging.info(output.strip())
            error = process.stderr.readline()
            if error:
                logging.error(error.strip())
            
            # Check if process has ended
            if output == '' and error == '' and process.poll() is not None:
                break
            
        return process.poll() == 0
    except Exception as e:
        logging.error(f"Command failed: {e}")
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
    
    # Combine commands to run Flask app
    if is_windows:
        full_command = f"{activate_cmd} && {python_cmd} run.py"
    else:
        full_command = f"{activate_cmd} && {python_cmd} run.py"
    
    logging.info("Starting Flask server...")
    if run_command(full_command):
        logging.info("Server stopped successfully")
    else:
        logging.error("Server failed to start or crashed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 