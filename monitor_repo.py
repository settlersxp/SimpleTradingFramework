import os
import time
import subprocess
import sys
import signal
import psutil
from git import Repo, GitCommandError
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

REPO_URL = "git@github.com:settlersxp/SimpleTradingFramework.git"
REPO_PATH = "SimpleTradingFramework"
CHECK_INTERVAL = 300  # 5 minutes in seconds

def kill_server_app():
    """Kill the Flask application process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if this is our Flask app
            if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0] and 'run.py' in proc.info['cmdline'][-1]:
                logging.info(f"Killing Flask app process (PID: {proc.info['pid']})")
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])])
                else:
                    os.kill(proc.info['pid'], signal.SIGTERM)
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def clone_repo():
    """Clone the repository if it doesn't exist"""
    if not os.path.exists(REPO_PATH):
        logging.info(f"Cloning repository from {REPO_URL}")
        try:
            Repo.clone_from(REPO_URL, REPO_PATH)
            logging.info("Repository cloned successfully")
        except GitCommandError as e:
            logging.error(f"Failed to clone repository: {e}")
            sys.exit(1)

def check_for_updates():
    """Check for updates in the repository"""
    try:
        repo = Repo(REPO_PATH)
        current_hash = repo.head.commit.hexsha
        
        # Fetch updates from remote
        origin = repo.remotes.origin
        origin.fetch()
        
        # Get the hash of the remote master branch
        remote_hash = origin.refs.master.commit.hexsha
        
        if current_hash != remote_hash:            
            # Kill the Server app
            if kill_server_app():
                logging.info("Server app terminated successfully")
            else:
                logging.warning("Server app process not found")
            
            # Pull changes
            origin.pull()
            
            return True
        
        return False
        
    except GitCommandError as e:
        logging.error(f"Git operation failed: {e}")
        return False

def run_command(command):
    """Run a command and return the output"""
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def main():
    # Initial setup
    clone_repo()
    
    logging.info("Starting repository monitor")
    
    while True:
        try:
            if check_for_updates():
                logging.info("Updates applied successfully")
            else:
                logging.info("No updates found")
                
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