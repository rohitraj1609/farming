from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for utils import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger, log_startup, log_success, log_error, log_warning, log_info
from utils.chatbot_prompt import get_system_prompt, get_user_prompt_template, validate_response_for_hallucination

# Import Ollama for local LLM
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    # Will log warning after logger is initialized

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = setup_logger("FarmingApp")

# Log Ollama availability status
if not OLLAMA_AVAILABLE:
    log_warning("Ollama not installed. Chatbot will use fallback responses. Install with: pip install ollama")

# Chatbot session storage (in-memory, stores conversation history per session)
chatbot_sessions = {}  # Format: {session_id: [{"role": "user", "content": "message"}, {"role": "assistant", "content": "response"}, ...]}

app = Flask(__name__, template_folder='../templates')

# Check required environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    log_error("SECRET_KEY environment variable is not set. Please check your .env file.")
    raise ValueError("SECRET_KEY environment variable is not set. Please check your .env file.")

MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    log_error("MONGO_URI environment variable is not set. Please check your .env file.")
    raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")

# Set Flask secret key
app.secret_key = SECRET_KEY
log_success("Flask secret key configured")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db_name = os.getenv('DB_NAME', 'farming')
    db = client[db_name]
    users_collection = db.users
    market_updates_collection = db.market_updates
    crops_collection = db.crops
    log_success(f"Connected to MongoDB database: {db_name}")
except Exception as e:
    log_error(f"Failed to connect to MongoDB: {e}")
    raise

# Market Updates Database Functions
def get_market_updates():
    """Get all market updates from database"""
    try:
        updates = list(market_updates_collection.find().sort("created_at", -1))
        for update in updates:
            update['_id'] = str(update['_id'])
        return updates
    except Exception as e:
        logger.error(f"Error getting market updates: {e}")
        return []

def add_market_update(update_data):
    """Add a new market update to database"""
    try:
        update_data['created_at'] = datetime.utcnow()
        result = market_updates_collection.insert_one(update_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error adding market update: {e}")
        return None

def update_market_update(update_id, update_data):
    """Update an existing market update"""
    try:
        from bson import ObjectId
        result = market_updates_collection.update_one(
            {"_id": ObjectId(update_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating market update: {e}")
        return False

def delete_market_update(update_id):
    """Delete a market update"""
    try:
        from bson import ObjectId
        result = market_updates_collection.delete_one({"_id": ObjectId(update_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting market update: {e}")
        return False

# Crops Database Functions
def get_crops(filters=None):
    """Get all crops from database with optional filters"""
    try:
        query = {}
        if filters:
            if filters.get('category'):
                query['category'] = filters['category']
            if filters.get('location'):
                query['location'] = {'$regex': filters['location'], '$options': 'i'}
            if filters.get('price_min') or filters.get('price_max'):
                price_query = {}
                if filters.get('price_min'):
                    price_query['$gte'] = filters['price_min']
                if filters.get('price_max'):
                    price_query['$lte'] = filters['price_max']
                query['price_per_kg'] = price_query
        
        crops = list(crops_collection.find(query).sort("created_at", -1))
        for crop in crops:
            crop['_id'] = str(crop['_id'])
            # Ensure all required fields exist with defaults
            crop.setdefault('total_price', crop.get('quantity', 0) * crop.get('price_per_kg', 0))
            crop.setdefault('seller_name', 'Unknown')
            crop.setdefault('seller_phone', '')
            crop.setdefault('description', '')
        return crops
    except Exception as e:
        logger.error(f"Error getting crops: {e}")
        return []

def add_crop(crop_data):
    """Add a new crop listing to database"""
    try:
        crop_data['created_at'] = datetime.utcnow()
        result = crops_collection.insert_one(crop_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error adding crop: {e}")
        return None

def update_crop(crop_id, crop_data):
    """Update an existing crop listing"""
    try:
        from bson import ObjectId
        result = crops_collection.update_one(
            {"_id": ObjectId(crop_id)},
            {"$set": crop_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating crop: {e}")
        return False

def delete_crop(crop_id):
    """Delete a crop listing"""
    try:
        from bson import ObjectId
        result = crops_collection.delete_one({"_id": ObjectId(crop_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting crop: {e}")
        return False

def get_user_crops(user_email):
    """Get crops listed by a specific user"""
    try:
        crops = list(crops_collection.find({"seller_email": user_email}).sort("created_at", -1))
        for crop in crops:
            crop['_id'] = str(crop['_id'])
            # Ensure all required fields exist with defaults
            crop.setdefault('total_price', crop.get('quantity', 0) * crop.get('price_per_kg', 0))
            crop.setdefault('seller_name', 'Unknown')
            crop.setdefault('seller_phone', '')
            crop.setdefault('description', '')
        return crops
    except Exception as e:
        logger.error(f"Error getting user crops: {e}")
        return []

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    # Check if it's a valid Indian phone number (10 digits)
    return len(phone_digits) == 10 and phone_digits.isdigit()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@app.route('/')
def index():
    """Serve the main webpage"""
    try:
        # Check if user is logged in, if so redirect to booking
        if 'user_id' in session:
            logger.info(f"User {session.get('username', 'Unknown')} is logged in, redirecting to booking page")
            return redirect('/booking')
        
        logger.info("Serving main webpage")
        return render_template('landing.html')
    except Exception as e:
        logger.error(f"Error serving main webpage: {e}")
        return "Error loading webpage.", 500

@app.route('/styles.css')
def styles():
    """Serve the CSS file"""
    try:
        # Get the correct path to the CSS file
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, '..', 'webpage', 'styles.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        return css_content, 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        logger.error(f"CSS file not found at: {css_path}")
        return "CSS file not found.", 404

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No content response

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        # Get the correct path to the JavaScript file
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, '..', 'webpage', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        logger.info("Serving JavaScript file")
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        logger.error(f"JavaScript file not found at: {js_path}")
        return "JavaScript file not found.", 404

@app.route('/static/js/<path:filename>')
def static_js(filename):
    """Serve static JavaScript files"""
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, '..', 'static', 'js', filename)
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        logger.info(f"Serving static JavaScript file: {filename}")
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        logger.error(f"Static JavaScript file not found: {filename}")
        return "JavaScript file not found.", 404


@app.route('/login-page')
def login_page():
    """Serve the login page only"""
    try:
        logger.info("Serving login page")
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error serving login page: {e}")
        return "Error loading login page.", 500

@app.route('/signup-page')
def signup_page():
    """Serve the signup page only"""
    try:
        logger.info("Serving signup page")
        return render_template('signup.html')
    except Exception as e:
        logger.error(f"Error serving signup page: {e}")
        return "Error loading signup page.", 500

@app.route('/about')
def about_page():
    """Serve the about us page"""
    try:
        logger.info("Serving about page")
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error serving about page: {e}")
        return "Error loading about page.", 500

@app.route('/profile-setup')
def profile_setup():
    """Serve the profile setup page"""
    try:
        logger.info(f"Profile setup accessed. Session: {dict(session)}")
        
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to profile setup - redirecting to login")
            flash('Please login to access profile setup', 'error')
            return redirect('/login-page')
        
        logger.info(f"Profile setup page served successfully")
        return render_template('profile_setup.html')
        
    except Exception as e:
        logger.error(f"Error serving profile setup page: {e}")
        return f"Error loading profile setup page: {e}", 500

@app.route('/complete-profile', methods=['POST'])
def complete_profile():
    """Handle profile completion form submission"""
    try:
        if 'user_id' not in session:
            flash('Please login to complete your profile', 'error')
            return redirect('/login-page')
        
        # Get form data
        name = request.form.get('name')
        location = request.form.get('location')
        bio = request.form.get('bio')
        
        logger.info(f"Profile completion for user: {session.get('email')}")
        
        # Validate required fields
        if not name or not location:
            flash('❌ Please fill in your name and farm location', 'error')
            return redirect('/profile-setup')
        
        # Update user profile in database
        user_id = session['user_id']
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'profile.name': name,
                    'profile.location': location,
                    'profile.bio': bio or '',
                    'profile_completed': True
                }
            }
        )
        
        # Update session
        session['profile'] = {
            'name': name,
            'location': location,
            'bio': bio or ''
        }
        
        # Add JavaScript to store user data in sessionStorage
        flash('🎉 Profile completed successfully! Welcome to CropMarket!', 'success')
        logger.info(f"✅ Profile completed for user: {session.get('email')}")
        
        # Redirect to booking page with user data
        response = redirect('/booking')
        return response
        
    except Exception as e:
        logger.error(f"Error completing profile: {e}")
        flash('❌ An error occurred. Please try again.', 'error')
        return redirect('/profile-setup')

@app.route('/booking')
def booking_page():
    """Serve the booking page"""
    try:
        logger.info(f"Booking page accessed. Session: {dict(session)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to booking page - redirecting to login")
            flash('Please login to access the booking page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        logger.info(f"Serving booking page for user: {user_name}")
        return render_template('booking.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio)
    except Exception as e:
        logger.error(f"Error serving booking page: {e}")
        return "Error loading booking page.", 500

@app.route('/sell')
def sell_page():
    """Sell crops page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to sell page - redirecting to login")
            flash('Please login to access the sell page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get user's own crop listings
        user_crops = get_user_crops(user_email)
        
        logger.info(f"Serving sell page for user: {user_name}")
        return render_template('sell.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
                             user_crops=user_crops)
    except Exception as e:
        logger.error(f"Error serving sell page: {e}")
        return "Error loading sell page.", 500

@app.route('/market')
def market_page():
    """Market updates page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to market page - redirecting to login")
            flash('Please login to access the market page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get market updates from database
        market_updates = get_market_updates()
        
        logger.info(f"Serving market page for user: {user_name}")
        return render_template('market.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
                             market_updates=market_updates)
    except Exception as e:
        logger.error(f"Error serving market page: {e}")
        return "Error loading market page.", 500

@app.route('/buy')
def buy_page():
    """Buy crops page"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning("Unauthorized access to buy page - redirecting to login")
            flash('Please login to access the buy page', 'error')
            return redirect('/login-page')
        
        # Get user data from session
        user_email = session.get('email', 'user@example.com')
        user_phone = session.get('phone', '')
        profile = session.get('profile', {})
        user_name = profile.get('name', user_email.split('@')[0])
        user_location = profile.get('location', '')
        user_bio = profile.get('bio', '')
        
        # Get crops from database with filters
        filters = {}
        category = request.args.get('category')
        location = request.args.get('location')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        
        if category:
            filters['category'] = category
        if location:
            filters['location'] = location
        if price_min is not None:
            filters['price_min'] = price_min
        if price_max is not None:
            filters['price_max'] = price_max
        
        crops = get_crops(filters)
        
        logger.info(f"Serving buy page for user: {user_name}")
        return render_template('buy.html', 
                             user_email=user_email,
                             user_phone=user_phone,
                             user_name=user_name,
                             user_location=user_location,
                             user_bio=user_bio,
                             crops=crops)
    except Exception as e:
        logger.error(f"Error serving buy page: {e}")
        return "Error loading buy page.", 500

@app.route('/test-booking')
def test_booking():
    """Test route to check if booking page works"""
    return "Booking page test - this should work!"

@app.route('/debug-session')
def debug_session():
    """Debug route to check session data"""
    return f"Session data: {dict(session)}"

# Market Updates API Routes
@app.route('/api/market-updates', methods=['GET'])
def api_get_market_updates():
    """Get all market updates"""
    try:
        updates = get_market_updates()
        return jsonify({"success": True, "updates": updates})
    except Exception as e:
        logger.error(f"Error getting market updates: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market-updates', methods=['POST'])
def api_add_market_update():
    """Add a new market update"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'category', 'description', 'impact']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        user_name = session.get('profile', {}).get('name', user_email.split('@')[0])
        
        # Create update data
        update_data = {
            'title': data['title'],
            'category': data['category'],
            'description': data['description'],
            'impact': data['impact'],
            'source': data.get('source', ''),
            'author': user_name,
            'author_email': user_email,
            'created_at': datetime.utcnow()
        }
        
        # Add to database
        update_id = add_market_update(update_data)
        
        if update_id:
            update_data['_id'] = update_id
            return jsonify({"success": True, "update": update_data})
        else:
            return jsonify({"success": False, "error": "Failed to add market update"}), 500
            
    except Exception as e:
        logger.error(f"Error adding market update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market-updates/<update_id>', methods=['PUT'])
def api_update_market_update(update_id):
    """Update a market update"""
    try:
        data = request.get_json()
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the author
        from bson import ObjectId
        update = market_updates_collection.find_one({"_id": ObjectId(update_id)})
        if not update:
            return jsonify({"success": False, "error": "Market update not found"}), 404
        
        if update.get('author_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to edit this update"}), 403
        
        # Update data
        update_data = {
            'title': data.get('title', update['title']),
            'category': data.get('category', update['category']),
            'description': data.get('description', update['description']),
            'impact': data.get('impact', update['impact']),
            'source': data.get('source', update.get('source', '')),
            'updated_at': datetime.utcnow()
        }
        
        success = update_market_update(update_id, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Market update updated successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to update market update"}), 500
            
    except Exception as e:
        logger.error(f"Error updating market update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/market-updates/<update_id>', methods=['DELETE'])
def api_delete_market_update(update_id):
    """Delete a market update"""
    try:
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the author
        from bson import ObjectId
        update = market_updates_collection.find_one({"_id": ObjectId(update_id)})
        if not update:
            return jsonify({"success": False, "error": "Market update not found"}), 404
        
        if update.get('author_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to delete this update"}), 403
        
        success = delete_market_update(update_id)
        
        if success:
            return jsonify({"success": True, "message": "Market update deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete market update"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting market update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Crops API Routes
@app.route('/api/crops', methods=['GET'])
def api_get_crops():
    """Get all crops with optional filters"""
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        location = request.args.get('location')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        
        filters = {}
        if category:
            filters['category'] = category
        if location:
            filters['location'] = location
        if price_min is not None:
            filters['price_min'] = price_min
        if price_max is not None:
            filters['price_max'] = price_max
        
        crops = get_crops(filters)
        return jsonify({"success": True, "crops": crops})
    except Exception as e:
        logger.error(f"Error getting crops: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crops', methods=['POST'])
def api_add_crop():
    """Add a new crop listing"""
    try:
        data = request.get_json()
        logger.info(f"Received crop data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'category', 'quantity', 'price_per_kg', 'location', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                logger.error(f"Missing required field: {field}")
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        user_name = session.get('profile', {}).get('name', user_email.split('@')[0])
        
        # Create crop data
        crop_data = {
            'name': data['name'],
            'category': data['category'],
            'quantity': int(data['quantity']),
            'price_per_kg': float(data['price_per_kg']),
            'total_price': int(data['quantity']) * float(data['price_per_kg']),
            'location': data['location'],
            'description': data['description'],
            'seller_name': user_name,
            'seller_email': user_email,
            'seller_phone': session.get('phone', ''),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        # Add to database
        crop_id = add_crop(crop_data)
        
        if crop_id:
            crop_data['_id'] = crop_id
            return jsonify({"success": True, "crop": crop_data})
        else:
            return jsonify({"success": False, "error": "Failed to add crop listing"}), 500
            
    except Exception as e:
        logger.error(f"Error adding crop: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crops/<crop_id>', methods=['PUT'])
def api_update_crop(crop_id):
    """Update a crop listing"""
    try:
        data = request.get_json()
        
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the seller
        from bson import ObjectId
        crop = crops_collection.find_one({"_id": ObjectId(crop_id)})
        if not crop:
            return jsonify({"success": False, "error": "Crop listing not found"}), 404
        
        if crop.get('seller_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to edit this listing"}), 403
        
        # Update data
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'category' in data:
            update_data['category'] = data['category']
        if 'quantity' in data:
            update_data['quantity'] = int(data['quantity'])
        if 'price_per_kg' in data:
            update_data['price_per_kg'] = float(data['price_per_kg'])
        if 'location' in data:
            update_data['location'] = data['location']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'is_active' in data:
            update_data['is_active'] = data['is_active']
        
        # Recalculate total price if quantity or price changed
        if 'quantity' in update_data or 'price_per_kg' in update_data:
            quantity = update_data.get('quantity', crop['quantity'])
            price_per_kg = update_data.get('price_per_kg', crop['price_per_kg'])
            update_data['total_price'] = quantity * price_per_kg
        
        update_data['updated_at'] = datetime.utcnow()
        
        success = update_crop(crop_id, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Crop listing updated successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to update crop listing"}), 500
            
    except Exception as e:
        logger.error(f"Error updating crop: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crops/<crop_id>', methods=['DELETE'])
def api_delete_crop(crop_id):
    """Delete a crop listing"""
    try:
        # Get user info from session
        user_email = session.get('email', 'anonymous@example.com')
        
        # Check if user is the seller
        from bson import ObjectId
        crop = crops_collection.find_one({"_id": ObjectId(crop_id)})
        if not crop:
            return jsonify({"success": False, "error": "Crop listing not found"}), 404
        
        if crop.get('seller_email') != user_email:
            return jsonify({"success": False, "error": "Unauthorized to delete this listing"}), 403
        
        success = delete_crop(crop_id)
        
        if success:
            return jsonify({"success": True, "message": "Crop listing deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete crop listing"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting crop: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test-booking-simple')
def test_booking_simple():
    """Simple test route for booking page without auth"""
    return "Booking page test - accessible without auth"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('index'))
        
        # Find user in database by email
        user = users_collection.find_one({'email': email})
        
        if user:
            logger.info(f"User found: {email}")
            logger.info(f"Stored password hash: {user['password'][:20]}...")
            logger.info(f"Provided password: {password}")
            
            password_match = check_password_hash(user['password'], password)
            logger.info(f"Password match: {password_match}")
            
            if password_match:
                session['user_id'] = str(user['_id'])
                session['email'] = user['email']
                session['phone'] = user.get('phone', '')
                session['username'] = user.get('username', user['email'])
                session['profile'] = user.get('profile', {})
                flash('🎉 Login successful! Welcome back!', 'success')
                logger.info(f"✅ User {email} logged in successfully, redirecting to booking page")
                logger.info(f"Session data: {dict(session)}")
                # Use direct URL redirect to booking page
                return redirect('/booking')
            else:
                flash('❌ Invalid password. Please check your password and try again.', 'error')
                logger.warning(f"Password mismatch for user: {email}")
                return redirect(url_for('index'))
        else:
            flash('❌ User not found. Please check your email or sign up for a new account.', 'error')
            logger.warning(f"User not found: {email}")
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    logger.info(f"Signup attempt for email: {email}, phone: {phone}")
    
    # Validation
    if not all([email, phone, password, confirm_password]):
        flash('Please fill in all fields', 'error')
        logger.warning("Signup failed: Missing fields")
        return redirect(url_for('signup_page'))
    
    if not validate_email(email):
        flash('❌ Please enter a valid email address (e.g., user@example.com)', 'error')
        logger.warning(f"Signup failed: Invalid email: {email}")
        return redirect(url_for('signup_page'))
    
    if not validate_phone(phone):
        flash('❌ Please enter a valid 10-digit phone number (e.g., 9876543210)', 'error')
        logger.warning(f"Signup failed: Invalid phone: {phone}")
        return redirect(url_for('signup_page'))
    
    if password != confirm_password:
        flash('❌ Passwords do not match. Please make sure both password fields are identical.', 'error')
        logger.warning(f"Signup failed: Password mismatch for email: {email}")
        return redirect(url_for('signup_page'))
    
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        flash(f'❌ {password_error}', 'error')
        logger.warning(f"Signup failed: {password_error} for email: {email}")
        return redirect(url_for('signup_page'))
    
    # Check if user already exists
    existing_user = users_collection.find_one({
        '$or': [
            {'email': email},
            {'phone': phone}
        ]
    })
    
    if existing_user:
        if existing_user['email'] == email:
            flash('❌ This email is already registered. Please use a different email or try logging in.', 'error')
        else:
            flash('❌ This phone number is already registered. Please use a different phone number.', 'error')
        logger.warning(f"Signup failed: User already exists - email: {email}, phone: {phone}")
        return redirect(url_for('signup_page'))
    
    # Create new user
    try:
        hashed_password = generate_password_hash(password)
        logger.info(f"Creating user: {email}")
        logger.info(f"Hashed password: {hashed_password[:20]}...")
        
        # Generate a unique username if email is already taken as username
        username = email
        counter = 1
        while users_collection.find_one({'username': username}):
            username = f"{email}_{counter}"
            counter += 1
        
        user_data = {
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'username': username,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True,
            'profile': {
                'name': '',
                'location': '',
                'bio': ''
            }
        }
        
        result = users_collection.insert_one(user_data)
        if result.inserted_id:
            # Store user info in session for profile completion
            session['user_id'] = str(result.inserted_id)
            session['email'] = email
            session['phone'] = phone
            session['username'] = username
            session['profile'] = user_data['profile']
            flash('🎉 Account created successfully! Please complete your profile.', 'success')
            logger.info(f"✅ New user registered successfully: {email} ({phone})")
            return redirect('/profile-setup')
        else:
            flash('❌ Failed to create account. Please try again.', 'error')
            logger.error(f"❌ Failed to create account for: {email}")
            return redirect(url_for('signup_page'))
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Signup error for {email}: {error_msg}")
        
        # Handle specific MongoDB errors
        if "E11000" in error_msg and "email" in error_msg:
            flash('❌ This email is already registered. Please use a different email or try logging in.', 'error')
        elif "E11000" in error_msg and "phone" in error_msg:
            flash('❌ This phone number is already registered. Please use a different phone number.', 'error')
        elif "E11000" in error_msg and "username" in error_msg:
            flash('❌ This email is already registered as a username. Please try logging in instead.', 'error')
        elif "E11000" in error_msg:
            flash('❌ Account already exists with this information. Please try logging in instead.', 'error')
        else:
            flash('❌ An error occurred while creating your account. Please try again.', 'error')
        
        return redirect(url_for('signup_page'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard', 'error')
        return redirect(url_for('index'))
    
    # Update last login time
    users_collection.update_one(
        {'_id': session['user_id']},
        {'$set': {'last_login': datetime.utcnow()}}
    )
    
    # Redirect to booking page after successful login
    logger.info(f"User {session.get('username', 'Unknown')} logged in - redirecting to booking page")
    return redirect(url_for('booking_page'))

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    logger.info(f"User {username} is logging out")
    
    # Clear the session
    session.clear()
    
    # Flash success message
    flash('👋 You have been successfully logged out!', 'success')
    
    logger.info(f"✅ User {username} logged out successfully")
    return redirect(url_for('index'))

@app.route('/api/users')
def api_users():
    """API endpoint to get all users (for testing)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = list(users_collection.find({}, {'password': 0}))
    for user in users:
        user['_id'] = str(user['_id'])
        if user.get('created_at'):
            user['created_at'] = user['created_at'].isoformat()
        if user.get('last_login'):
            user['last_login'] = user['last_login'].isoformat()
    
    return jsonify(users)

def detect_language(text):
    """
    Detects the language of the user's message.
    Returns: 'en' (English), 'hi' (Hindi), or 'hinglish' (Hinglish)
    
    Special handling:
    - If message is ONLY a greeting, detect the language of the greeting itself
    - If message contains greeting + other content, detect language from non-greeting part
    """
    if not text:
        return 'en'  # Default to English
    
    # English greetings (40)
    english_greetings = [
        'hello', 'hi', 'hey', 'greetings', 'goodbye', 'bye', 'farewell', 'later', 'adieu', 'welcome',
        'good morning', 'good afternoon', 'good evening', 'morning', 'afternoon', 'evening',
        'good day', 'good night', 'have a good one', 'safe travels',
        'hiya', 'howdy', 'yo', 'sup', 'what\'s up', 'cheers', 'g\'day', 'alright', 
        'mate', 'man', 'dude', 'boss', 'chief', 'buddy', 'catch ya',
        'dear', 'respectfully', 'my respects', 'how do you do', 'to whom it may concern',
        'kind regards', 'blessings', 'salutations'
    ]
    
    # Hindi greetings (30) - in transliteration
    hindi_greetings = [
        'namaste', 'namaskar', 'pranam', 'suprabhaat', 'shubh apraahna', 'shubh sandhya',
        'shubh raatri', 'swagat', 'aaiye', 'vidai', 'alvida', 'phir milenge',
        'dhanyavaad', 'shukriya', 'kshama', 'maaf karna', 'kripya',
        'jai shri ram', 'radhe radhe', 'jai hind', 'sat sri akaal',
        'as-salaam-alaikum', 'aadab', 'bhai', 'behan', 'mitra', 'mubarak',
        'padhariye', 'kushal mangal', 'ram ram'
    ]
    
    # Hinglish greetings (30)
    hinglish_greetings = [
        'hello yaar', 'hi bhai', 'kya up', 'good', 'bye milte hain', 'chal bye',
        'haan boss', 'achcha okay', 'morning ji', 'everything is theek',
        'what chal raha hai', 'aur', 'same to same', 'thora busy', 'sab cool',
        'chalo party', 'take care phir', 'thanks yaar', 'absolutely boss',
        'hota hai', 'oh waah', 'pakka', 'no worries bhai', 'kya scene hai',
        'long time no see', 'i am coming', 'you going na', 'done hai', 'just chill',
        'bye for now', 'kaise ho', 'kaise hain', 'kya haal hai', 'kya chal raha hai'
    ]
    
    # Combined list for checking
    all_greetings = english_greetings + hindi_greetings + hinglish_greetings
    
    # Normalize text for comparison
    text_lower = text.lower().strip()
    
    # Check if message is ONLY a greeting (with optional punctuation)
    text_for_check = re.sub(r'[^\w\s]', '', text_lower)  # Remove punctuation
    words = text_for_check.split()
    
    # Check if all words are greetings
    is_only_greeting = False
    greeting_language = None
    
    if len(words) <= 4:  # Greetings are usually short (1-4 words)
        # Check if the entire phrase matches a greeting
        phrase = ' '.join(words)
        
        # Check against multi-word greetings first
        if phrase in hinglish_greetings:
            is_only_greeting = True
            greeting_language = 'hinglish'
        elif phrase in hindi_greetings:
            is_only_greeting = True
            greeting_language = 'hi'
        elif phrase in english_greetings:
            is_only_greeting = True
            greeting_language = 'en'
        else:
            # Check individual words
            all_greetings = True
            has_english_greeting = False
            has_hindi_greeting = False
            has_hinglish_greeting = False
            
            for word in words:
                if len(word) <= 2:  # Skip very short words
                    continue
                if word in english_greetings:
                    has_english_greeting = True
                elif word in hindi_greetings:
                    has_hindi_greeting = True
                elif word in hinglish_greetings:
                    has_hinglish_greeting = True
                else:
                    all_greetings = False
                    break
            
            if all_greetings:
                is_only_greeting = True
                # Determine language based on greeting type found
                if has_hinglish_greeting:
                    greeting_language = 'hinglish'
                elif has_hindi_greeting:
                    greeting_language = 'hi'
                elif has_english_greeting:
                    greeting_language = 'en'
                else:
                    greeting_language = 'en'  # Default
    
    # If it's only a greeting, return the language of the greeting
    if is_only_greeting and greeting_language:
        logger.info(f"Message detected as greeting only: '{text}' - detected language: {greeting_language}")
        return greeting_language
    
    # If message contains greeting + other content, remove greeting words and detect from remaining text
    remaining_words = []
    for word in words:
        clean_word = re.sub(r'[^\w\u0900-\u097F]', '', word.lower())
        if clean_word and clean_word not in all_greetings:
            # Also check if it's part of a multi-word greeting
            is_greeting_word = False
            for greeting in all_greetings:
                if clean_word in greeting.split():
                    is_greeting_word = True
                    break
            if not is_greeting_word:
                remaining_words.append(word)
    
    # If we have remaining words after removing greetings, use those for detection
    if remaining_words:
        text_for_detection = ' '.join(remaining_words)
        logger.info(f"Message contains greeting + content. Detecting from: '{text_for_detection}'")
    else:
        # If no remaining words (shouldn't happen, but fallback)
        text_for_detection = text
    
    # Check for Devanagari script (Hindi characters)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    has_hindi = bool(devanagari_pattern.search(text_for_detection))
    
    # Check for English characters (letters)
    english_pattern = re.compile(r'[a-zA-Z]')
    has_english = bool(english_pattern.search(text_for_detection))
    
    # Count words in the detection text
    detection_words = text_for_detection.split()
    hindi_words = 0
    english_words = 0
    
    for word in detection_words:
        # Remove punctuation for checking
        clean_word = re.sub(r'[^\w\u0900-\u097F]', '', word)
        if not clean_word:
            continue
        
        if devanagari_pattern.search(clean_word):
            hindi_words += 1
        elif english_pattern.search(clean_word):
            english_words += 1
    
    # Determine language
    if has_hindi and has_english:
        return 'hinglish'
    elif has_hindi:
        return 'hi'
    else:
        return 'en'  # Default to English if no Hindi detected

def clean_instruction_leakage(text):
    """
    Removes instruction-like text, meta-commentary, or parenthetical explanations that might leak from prompts.
    """
    if not text:
        return text
    
    # Patterns to remove (instruction-like phrases and parenthetical notes)
    patterns_to_remove = [
        r'\([^)]*(?:check|respond|guide|instruction|language|accordingly|please|tell me)[^)]*\)',
        r'\([^)]*(?:I am|I\'m) an? [^)]*assistant[^)]*\)',
        r'\([^)]*(?:Please|please)[^)]*(?:guide|check|respond|tell)[^)]*\)',
        r'Check the user\'s language and respond accordingly',
        r'Please guide me on how',
        r'\(.*?\)',  # Remove any remaining parenthetical notes
    ]
    
    cleaned = text
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up multiple spaces, newlines, and periods
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)
    cleaned = re.sub(r'\.\s*\.+', '.', cleaned)  # Remove multiple periods
    cleaned = re.sub(r'\s+\.', '.', cleaned)  # Remove space before period
    
    return cleaned.strip()

def remove_repetitive_content(text):
    """
    Detects and removes repetitive sentences/phrases from the response.
    Returns cleaned text with duplicates removed.
    """
    if not text:
        return text
    
    # Split text into sentences (by periods, exclamation marks, question marks, newlines)
    sentences = re.split(r'[.!?\n]\s+', text)
    
    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]  # Ignore very short fragments
    
    if len(sentences) < 2:
        return text
    
    # Track seen sentences (normalized for comparison)
    seen = set()
    unique_sentences = []
    sentence_counts = {}  # Track how many times we've seen similar sentences
    
    for sentence in sentences:
        # Normalize sentence for comparison (lowercase, remove extra spaces)
        normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
        
        # Skip if sentence is too short
        if len(normalized) < 15:
            unique_sentences.append(sentence)
            continue
        
        # Check if this sentence is similar to any seen sentence (75% similarity threshold)
        is_duplicate = False
        best_match = None
        
        for seen_sentence in seen:
            # Simple similarity check: if one sentence contains most of the other
            words_current = set(normalized.split())
            words_seen = set(seen_sentence.split())
            
            if len(words_current) > 0 and len(words_seen) > 0:
                # Calculate overlap using Jaccard similarity
                intersection = len(words_current & words_seen)
                union = len(words_current | words_seen)
                similarity = intersection / union if union > 0 else 0
                
                if similarity > 0.75:  # 75% word overlap = likely duplicate
                    is_duplicate = True
                    best_match = seen_sentence
                    break
        
        if not is_duplicate:
            seen.add(normalized)
            unique_sentences.append(sentence)
            sentence_counts[normalized] = 1
        else:
            # Count how many times we've seen this
            if best_match in sentence_counts:
                sentence_counts[best_match] += 1
            else:
                sentence_counts[best_match] = 2
            
            # Only log if we've seen it multiple times
            if sentence_counts.get(best_match, 0) > 2:
                logger.debug(f"Removed duplicate sentence (seen {sentence_counts[best_match]} times): {sentence[:50]}...")
    
    # Rejoin sentences with periods
    cleaned_text = '. '.join(unique_sentences)
    
    # Ensure proper ending punctuation
    if cleaned_text and not cleaned_text[-1] in '.!?':
        cleaned_text += '.'
    
    return cleaned_text

# Chatbot API Route with Chain-of-Thought Reasoning
@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """Chatbot endpoint using local LLM with chain-of-thought reasoning"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', None)
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        # Create new session if session_id is not provided
        if not session_id:
            session_id = f"chat_{uuid.uuid4().hex[:16]}"
            logger.info(f"Created new chat session: {session_id}")
        
        # Initialize session if it doesn't exist
        if session_id not in chatbot_sessions:
            chatbot_sessions[session_id] = []
            logger.info(f"Initialized new session storage for: {session_id}")
        
        # Get conversation history from session storage
        session_history = chatbot_sessions[session_id]
        
        # Use provided history if available, otherwise use session history
        if not history and session_history:
            # Convert session history to the format expected by LLM
            history = []
            for msg in session_history[-10:]:  # Last 10 messages
                if msg.get('role') == 'user':
                    history.append({'user': msg.get('content', ''), 'assistant': ''})
                elif msg.get('role') == 'assistant':
                    if history and history[-1].get('user'):
                        history[-1]['assistant'] = msg.get('content', '')
                    else:
                        history.append({'user': '', 'assistant': msg.get('content', '')})
        
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Ollama is not installed. Please install it: pip install ollama",
                "response": "I'm sorry, the AI assistant is not available. Please install Ollama to enable AI features."
            }), 503
        
        # Detect language BEFORE processing with LLM
        detected_lang = detect_language(user_message)
        logger.info(f"Detected language for message '{user_message[:50]}...': {detected_lang}")
        
        # Get system prompt with language-specific instructions
        system_prompt = get_system_prompt(detected_lang)
        
        # Add context about available data sources
        context_info = ""
        
        # Check if we have crops in database to reference
        try:
            available_crops = get_crops()
            if available_crops:
                crop_names = list(set([c.get('name', '') for c in available_crops[:10] if c.get('name')]))
                if crop_names:
                    context_info = f"\n\nNote: The platform currently has listings for: {', '.join(crop_names[:5])}. "
                    context_info += "When users ask about specific crops, you can mention checking the Buy Crops page for current listings."
        except:
            pass  # If database query fails, continue without context
        
        # Add market updates context if available
        try:
            market_updates = get_market_updates()
            if market_updates:
                context_info += f"\nThere are {len(market_updates)} market updates available. Direct users to the Market Updates page for current information."
        except:
            pass
        
        # Combine system prompt with context
        full_system_prompt = system_prompt + context_info

        # Build conversation messages for Ollama (using session history)
        messages = [{'role': 'system', 'content': full_system_prompt}]
        
        # Add conversation history from session storage
        if session_history:
            # Convert session history to Ollama message format
            for msg in session_history[-10:]:  # Last 10 messages for context
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        'role': msg['role'],
                        'content': msg.get('content', '')
                    })
        
        # Add current user message with chain-of-thought instruction
        user_prompt_template = get_user_prompt_template()
        messages.append({
            'role': 'user',
            'content': user_prompt_template.format(user_message=user_message)
        })
        
        # Get model name from environment or use default
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        try:
            # Call Ollama with chain-of-thought reasoning and full conversation history
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    'temperature': 0.7,  # Slightly higher for more detailed, comprehensive responses
                    'top_p': 0.9,
                    'num_predict': 2000,  # Increased limit for detailed, comprehensive responses
                    'repeat_penalty': 1.2  # Penalty for repetition (higher = less repetition)
                }
            )
            
            bot_response = response['message']['content'].strip()
            
            # Clean instruction leakage and meta-commentary
            bot_response = clean_instruction_leakage(bot_response)
            
            # Detect and remove repetitive content
            bot_response = remove_repetitive_content(bot_response)
            
            # Validate response for potential hallucinations
            is_valid, warning = validate_response_for_hallucination(bot_response)
            if not is_valid and warning:
                logger.warning(f"Potential hallucination detected in response: {warning}")
                # Add a disclaimer to the response
                disclaimer = "\n\n> **Note:** For current market prices and specific data, please check the Market Updates page."
                if disclaimer not in bot_response:
                    bot_response += disclaimer
            
            # Preserve markdown formatting - don't remove markdown symbols
            # Only clean up excessive spaces (3+ spaces) but preserve markdown structure
            # Split by newlines to preserve structure
            lines = bot_response.split('\n')
            cleaned_lines = []
            for line in lines:
                # Clean up excessive spaces (3+ spaces) but keep markdown formatting
                cleaned_line = re.sub(r' {3,}', ' ', line)
                # Don't strip the line completely - preserve leading spaces for code blocks
                if cleaned_line.strip():  # Only add non-empty lines
                    cleaned_lines.append(cleaned_line)
                elif cleaned_line == '':  # Preserve empty lines for paragraph breaks
                    cleaned_lines.append('')
            
            # Rejoin with newlines to preserve markdown structure
            bot_response = '\n'.join(cleaned_lines)
            bot_response = bot_response.strip()
            
            # Store conversation in session history
            chatbot_sessions[session_id].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.utcnow().isoformat()
            })
            chatbot_sessions[session_id].append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Limit session history to last 50 messages to prevent memory issues
            if len(chatbot_sessions[session_id]) > 50:
                chatbot_sessions[session_id] = chatbot_sessions[session_id][-50:]
            
            logger.info(f"Chatbot response generated successfully for session: {session_id}")
            return jsonify({
                "success": True,
                "response": bot_response,
                "session_id": session_id
            })
            
        except Exception as ollama_error:
            logger.error(f"Ollama error: {ollama_error}")
            
            # Check if Ollama service is running
            if "connection" in str(ollama_error).lower() or "refused" in str(ollama_error).lower():
                return jsonify({
                    "success": False,
                    "error": "Ollama service is not running",
                    "response": "I'm sorry, the AI service is not running. Please make sure Ollama is installed and running. You can start it by running 'ollama serve' in your terminal."
                }), 503
            
            # Fallback response
            return jsonify({
                "success": False,
                "error": str(ollama_error),
                "response": "I'm having trouble processing your request right now. Please try again in a moment."
            }), 500
            
    except Exception as e:
        logger.error(f"Chatbot API error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I'm sorry, I encountered an error. Please try again."
        }), 500

if __name__ == '__main__':
    # Show startup banner
    log_startup()
    
    # Create indexes for better performance
    try:
        # Drop old username index if it exists
        try:
            users_collection.drop_index("username_1")
            log_info("Dropped old username index")
        except Exception as e:
            log_info(f"Username index drop result: {e}")
        
        # Clean up existing users with null usernames
        try:
            result = users_collection.update_many(
                {"username": None},
                {"$set": {"username": "$email"}}
            )
            if result.modified_count > 0:
                log_info(f"Updated {result.modified_count} users with null usernames")
        except Exception as e:
            log_warning(f"Error updating null usernames: {e}")
        
        # Create new indexes
        users_collection.create_index("email", unique=True)
        users_collection.create_index("phone", unique=True)
        # Create username index with sparse option to allow null values
        users_collection.create_index("username", unique=True, sparse=True)
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
    
    try:
        app.run(debug=debug_mode, host=host, port=port)
    except KeyboardInterrupt:
        log_info("Shutting down Farming App...")
        log_success("👋 Farming App stopped successfully!")
    except Exception as e:
        log_error(f"Farming App crashed: {e}")
        sys.exit(1)
