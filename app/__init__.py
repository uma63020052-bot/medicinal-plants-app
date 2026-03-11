"""
Flask App Initialization
Medicinal Plants Identification System
"""

from flask import Flask
from flask_cors import CORS
import os

def create_app():
    """Create and configure Flask app"""
    
    # Get the base directory (project root)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Create Flask app with correct template folder
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = 'medicinal-plants-sih-2023'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
    app.config['MODELS_FOLDER'] = os.path.join(base_dir, 'models')
    
    # Enable CORS for frontend
    CORS(app)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app