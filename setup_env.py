import os
import sys
import subprocess
import platform

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_pip():
    """Check if pip or pip3 exists and return the working command"""
    if run_command("pip --version"):
        return "pip"
    elif run_command("pip3 --version"):
        return "pip3"
    else:
        print("Error: Neither pip nor pip3 is installed.")
        sys.exit(1)

def main():
    # Determine the operating system
    is_windows = platform.system().lower() == "windows"
    venv_path = "venv"
    
    # Check if virtual environment exists
    if not os.path.exists(venv_path):
        print("Virtual environment not found. Creating one...")
        
        # Get pip command
        pip_cmd = check_pip()
        
        # Create virtual environment
        if not run_command(f"{pip_cmd} install virtualenv"):
            print("Error: Failed to install virtualenv")
            sys.exit(1)
            
        if not run_command(f"python -m venv {venv_path}"):
            print("Error: Failed to create virtual environment")
            sys.exit(1)
    
    # Activate virtual environment and install requirements
    if is_windows:
        activate_cmd = f"{venv_path}\\Scripts\\activate"
        pip_install_cmd = f"{venv_path}\\Scripts\\pip install -r requirements.txt"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
        pip_install_cmd = f"{venv_path}/bin/pip install -r requirements.txt"
    
    # Combine commands
    if is_windows:
        full_command = f"{activate_cmd} && {pip_install_cmd}"
    else:
        full_command = f"{activate_cmd} && {pip_install_cmd}"
    
    print("Activating virtual environment and installing requirements...")
    if not run_command(full_command):
        print("Error: Failed to install requirements")
        sys.exit(1)
    
    print("Setup completed successfully!")

if __name__ == "__main__":
    main() 