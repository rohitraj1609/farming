"""
🌱 FARMING APP - Agricultural Management Platform 🌱

Main entry point for the Farming App.
This script starts the Flask application with proper logging and error handling.

Usage:
    conda activate syed
    python main.py

Requirements:
    - Conda environment 'syed' activated
    - .env file with required environment variables
    - All dependencies installed via requirements.txt
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# Ensure conda environment is being used
conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
conda_prefix = os.environ.get('CONDA_PREFIX')

# Try to find and use 'syed' conda environment
if conda_env != 'syed':
    # Try to find syed environment
    if conda_prefix:
        # Check if syed environment exists in the same conda installation
        conda_base = os.path.dirname(os.path.dirname(conda_prefix)) if conda_prefix else None
        if conda_base:
            syed_env_path = os.path.join(conda_base, 'envs', 'syed')
            if os.path.exists(syed_env_path):
                # Use syed environment Python
                if sys.platform == 'win32':
                    syed_python = os.path.join(syed_env_path, 'python.exe')
                else:
                    syed_python = os.path.join(syed_env_path, 'bin', 'python')
                
                if os.path.exists(syed_python):
                    print(f"✅ Found 'syed' conda environment, switching to it...")
                    try:
                        os.execv(syed_python, [syed_python] + sys.argv)
                    except Exception as e:
                        print(f"❌ Error switching to syed environment: {e}")
                        sys.exit(1)
    
    # If syed not found, check current environment
    if conda_env:
        print(f"⚠️  Warning: Using conda environment '{conda_env}' instead of 'syed'")
        print(f"   Please activate the correct environment:")
        print("   conda activate syed")
        print("   Then run: python main.py")
        sys.exit(1)
    else:
        print("⚠️  Warning: No conda environment detected!")
        print("   Please activate conda environment first:")
        print("   conda activate syed")
        print("   Then run: python main.py")
        sys.exit(1)

# Verify we're using conda Python (handle Windows case sensitivity)
if conda_prefix:
    if sys.platform == 'win32':
        conda_python = os.path.join(conda_prefix, 'python.exe')
    else:
        conda_python = os.path.join(conda_prefix, 'bin', 'python')
    
    current_python = sys.executable
    
    # Normalize paths for comparison (handle Windows case sensitivity)
    def normalize_path(path):
        if sys.platform == 'win32':
            # Windows: normalize case and path
            return os.path.normpath(os.path.normcase(os.path.abspath(path)))
        return os.path.normpath(os.path.abspath(path))
    
    current_normalized = normalize_path(current_python)
    conda_normalized = normalize_path(conda_python)
    prefix_normalized = normalize_path(conda_prefix)
    
    # Check if we're using conda Python
    if not current_normalized.startswith(prefix_normalized):
        # Try to switch to conda Python if it exists
        if os.path.exists(conda_python):
            print(f"✅ Switching to conda Python: {conda_python}")
            try:
                # Use execv to replace current process with conda Python
                if sys.platform == 'win32':
                    os.execv(conda_python, [conda_python] + sys.argv)
                else:
                    os.execv(conda_python, [conda_python] + sys.argv)
            except Exception as e:
                print(f"❌ Error switching to conda Python: {e}")
                print(f"   Current Python: {current_python}")
                print(f"   Conda Python: {conda_python}")
                print(f"   Please run: conda activate syed && python main.py")
                sys.exit(1)
        else:
            print(f"⚠️  Warning: Conda Python not found at: {conda_python}")
            print(f"   Current Python: {current_python}")
            print(f"   Conda prefix: {conda_prefix}")
            print(f"   Please ensure conda environment 'syed' is activated")
            print("   Run: conda activate syed && python main.py")
            sys.exit(1)

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the Flask app
try:
    from backend.app import app, logger, log_startup, log_success, log_error, log_info, log_warning
    from pymongo import MongoClient
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()

    # Show startup banner
    log_startup()

    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        log_error(".env file not found! Please create a .env file with required variables.")
        log_info("Required variables: MONGO_URI, SECRET_KEY")
        sys.exit(1)

    log_success("Environment file found")

    # Check required environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        log_error("SECRET_KEY environment variable is not set. Please check your .env file.")
        sys.exit(1)

    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        log_error("MONGO_URI environment variable is not set. Please check your .env file.")
        sys.exit(1)

    # Test MongoDB connection
    try:
        client = MongoClient(MONGO_URI)
        db_name = os.getenv('DB_NAME', 'farming')
        db = client[db_name]
        # Test the connection
        client.admin.command('ping')
        log_success(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        log_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    # Create indexes for better performance
    try:
        users_collection = db.users
        users_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        log_success("Database indexes created successfully")
    except Exception as e:
        log_warning(f"Index creation warning: {e}")

    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    log_info(f"Starting Farming App server on {host}:{port}")
    log_info(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
    log_success("🌱 Farming App is ready! Press Ctrl+C to stop.")
    print(f"\n{'='*60}")
    print(f"🌐 ACCESS YOUR FARMING APP:")
    print(f"   Local:   http://localhost:{port}")
    print(f"   Network: http://127.0.0.1:{port}")
    print(f"   External: http://192.168.1.7:{port}")
    print(f"{'='*60}")
    print(f"💡 TIP: Click the links above or copy them to your browser!")
    print(f"{'='*60}\n")

    # Auto-open browser only once (check if already opened)
    browser_opened_file = current_dir / '.browser_opened'
    if not browser_opened_file.exists():
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')
            # Mark that browser was opened
            browser_opened_file.touch()

        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    else:
        log_info("Browser already opened previously - skipping auto-open")

    try:
        app.run(debug=debug_mode, host=host, port=port)
    except KeyboardInterrupt:
        log_info("Shutting down Farming App...")
        log_success("👋 Farming App stopped successfully!")
    except Exception as e:
        log_error(f"Farming App crashed: {e}")
        sys.exit(1)