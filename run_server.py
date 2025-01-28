import sys
import logging
from deployment_utils import run_command_as_subprocess_with_stream, \
                                register_logger, \
                                is_windows, \
                                get_venv_path


logger = register_logger('run_server')


def main():
    activate_cmd, python_cmd = get_venv_path(logger)

    # Combine commands to run Flask app
    if is_windows:
        full_command = f"{activate_cmd} && {python_cmd} run.py"
    else:
        full_command = f"{activate_cmd} && {python_cmd} run.py"

    logging.info("Starting Flask server...")
    if run_command_as_subprocess_with_stream(full_command, logging):
        logging.info("Server stopped successfully")
    else:
        logging.error("Server failed to start or crashed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
