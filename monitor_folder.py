import os
import time
import subprocess
import logging
from datetime import datetime
import sys
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('folder_monitor.log'),
        logging.StreamHandler()
    ]
)

FOLDER_PATH = "SimpleTradingFramework"
CHECK_INTERVAL = 10  # seconds
LAST_HASH_FILE = "last_folder_hash.txt"

def get_folder_hash():
    """Calculate hash of the entire folder contents"""
    if not os.path.exists(FOLDER_PATH):
        return None
        
    sha256_hash = hashlib.sha256()

    for root, dirs, files in os.walk(FOLDER_PATH):
        for names in files:
            filepath = os.path.join(root, names)
            try:
                with open(filepath, 'rb') as f:
                    for byte_block in iter(lambda: f.read(4096), b''):
                        sha256_hash.update(byte_block)
            except (IOError, PermissionError) as e:
                logging.warning(f"Couldn't read file {filepath}: {e}")
                continue

    return sha256_hash.hexdigest()

def save_hash(folder_hash):
    """Save the current folder hash"""
    with open(LAST_HASH_FILE, 'w') as f:
        f.write(folder_hash)

def get_saved_hash():
    """Get the last saved folder hash"""
    try:
        with open(LAST_HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def run_setup_scripts():
    """Run setup_env.py and setup_db.py"""
    scripts = ['setup_env.py', 'setup_db.py']
    
    for script in scripts:
        script_path = os.path.join(FOLDER_PATH, script)
        if not os.path.exists(script_path):
            logging.error(f"Script {script} not found!")
            continue
            
        logging.info(f"Running {script}...")
        try:
            # Use python executable from system path
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, script_path],
                check=True,
                capture_output=True,
                text=True
            )
            logging.info(f"{script} output:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"{script} errors:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running {script}: {e}")
            logging.error(f"Script output:\n{e.output}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error running {script}: {e}")
            continue
            
        logging.info(f"Successfully completed {script}")

def main():
    logging.info("Starting folder monitor")
    
    last_check_time = None
    
    while True:
        try:
            current_time = datetime.now()
            
            # Get current folder hash
            current_hash = get_folder_hash()
            saved_hash = get_saved_hash()
            
            # Check if folder exists
            if current_hash is None:
                logging.info(f"Folder {FOLDER_PATH} does not exist")
                time.sleep(CHECK_INTERVAL)
                continue
                
            # If this is the first time we're seeing the folder
            if saved_hash is None:
                logging.info("Folder created for the first time")
                run_setup_scripts()
                save_hash(current_hash)
                
            # If the folder has been modified
            elif current_hash != saved_hash:
                logging.info("Folder contents have changed")
                run_setup_scripts()
                save_hash(current_hash)
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logging.info("Monitor stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 