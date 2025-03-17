#!/usr/bin/env python
"""
Script to install Python requirements from requirements.txt without admin rights
"""
import os
import sys
import subprocess
import platform

def print_colored(text, color):
    """Print colored text in the terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'end': '\033[0m'
    }
    
    # Windows cmd doesn't support ANSI color codes by default
    if platform.system() == 'Windows' and not os.environ.get('TERM'):
        print(text)
    else:
        print(f"{colors.get(color, '')}{text}{colors['end']}")

def run_command(cmd):
    """Run a command and return the result and success status"""
    try:
        result = subprocess.run(
            cmd, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_venv():
    """Check if running in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print_colored("Warning: You're not running in a virtual environment.", "yellow")
        print_colored("It's recommended to use a virtual environment for Python projects.", "yellow")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

def install_requirements():
    """Install requirements from requirements.txt file"""
    if not os.path.exists('requirements.txt'):
        print_colored("Error: requirements.txt file not found in the current directory.", "red")
        sys.exit(1)
    
    print_colored("Attempting to install requirements from requirements.txt...", "cyan")
    
    # First attempt - standard installation
    success, output = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if success:
        print_colored("Requirements installed successfully!", "green")
        return True
    
    print_colored("Standard installation failed. Trying with --user flag...", "yellow")
    print_colored(f"Error details: {output}", "yellow")
    
    # Second attempt - with --user flag
    success, output = run_command([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
    if success:
        print_colored("Requirements installed successfully with --user flag!", "green")
        return True
    
    print_colored("Installation with --user flag failed.", "red")
    print_colored(f"Error details: {output}", "red")
    
    # Third attempt - try installing specific missing packages
    print_colored("\nTrying to install specific packages that might be missing...", "cyan")
    common_packages = ["flask", "requests", "pandas", "numpy", "matplotlib"]
    
    for package in common_packages:
        print_colored(f"Attempting to install {package}...", "cyan")
        success, _ = run_command([sys.executable, "-m", "pip", "install", package])
        if success:
            print_colored(f"{package} installed successfully!", "green")
    
    # Final suggestions
    print_colored("\nIf you're still having issues, try these steps:", "yellow")
    print_colored("1. Make sure your virtual environment is properly activated", "yellow")
    print_colored("2. Try upgrading pip: python -m pip install --upgrade pip", "cyan")
    print_colored("3. Try installing packages one by one:", "yellow")
    print_colored("   python -m pip install flask", "cyan")
    print_colored("4. Check if there are any network or proxy issues", "yellow")
    
    return False

def check_and_create_requirements():
    """Check if requirements.txt exists and create it with Flask if it doesn't"""
    if not os.path.exists('requirements.txt'):
        print_colored("requirements.txt not found. Creating one with Flask...", "yellow")
        with open('requirements.txt', 'w') as f:
            f.write("flask>=2.0.0\n")
        print_colored("Created requirements.txt with Flask dependency", "green")
    else:
        # Check if Flask is already in requirements.txt
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if not any(line.strip().lower().startswith('flask') for line in content.splitlines()):
            print_colored("Adding Flask to existing requirements.txt", "yellow")
            with open('requirements.txt', 'a') as f:
                f.write("\n# Added automatically\nflask>=2.0.0\n")
            print_colored("Flask added to requirements.txt", "green")

if __name__ == "__main__":
    check_venv()
    check_and_create_requirements()
    install_requirements() 