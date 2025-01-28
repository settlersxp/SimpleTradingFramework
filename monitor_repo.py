import os
import time
from git import Repo, GitCommandError
import logging
from deployment_utils import register_logger, kill_python_process
import sys

# Setup logging
logger = register_logger('monitor_repo')

REPO_URL = "git@github.com:settlersxp/SimpleTradingFramework.git"
REPO_PATH = "SimpleTradingFramework"
CHECK_INTERVAL = 300  # 5 minutes in seconds


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
            if kill_python_process():
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
