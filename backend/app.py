from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for utils import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger, log_startup, log_success, log_error, log_warning, log_info

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = setup_logger("FarmingApp")

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
        
        with open(css_path, 'r') as f:
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
        
        with open(js_path, 'r') as f:
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
        
        with open(js_path, 'r') as f:
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
        
        user_data = {
            'email': email,
            'phone': phone,
            'password': hashed_password,
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

if __name__ == '__main__':
    # Show startup banner
    log_startup()
    
    # Create indexes for better performance
    try:
        # Drop old username index if it exists
        try:
            users_collection.drop_index("username_1")
            log_info("Dropped old username index")
        except:
            pass  # Index doesn't exist, that's fine
        
        # Create new indexes
        users_collection.create_index("email", unique=True)
        users_collection.create_index("phone", unique=True)
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
