#!/usr/bin/env python3
"""
Wrapper script to set up Python path before importing the main app
This runs main.py with proper sys.path configuration
"""
import sys
import os

# Get the AppDir from the APPDIR environment variable set by AppRun
appdir = os.environ.get('APPDIR')
if not appdir:
    # Fallback for testing
    appdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

site_packages = os.path.join(appdir, 'usr/lib/python3/site-packages')

# Insert at the very beginning BEFORE any imports
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

# Now read and execute main.py directly
main_py = os.path.join(os.path.dirname(__file__), 'main.py')

# Read the main.py file
with open(main_py, 'r') as f:
    code = f.read()

# Execute it in the current namespace with proper sys.path already set
exec(code, {'__name__': '__main__', '__file__': main_py})
