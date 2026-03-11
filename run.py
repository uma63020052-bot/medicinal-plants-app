"""
Run Flask API Server
Medicinal Plants Identification System - Smart India Hackathon 2023
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.model_loader import get_model_loader

# Create Flask app
app = create_app()

# Load models on startup
print("\n" + "="*70)
print("MEDICINAL PLANTS IDENTIFICATION SYSTEM")
print("Smart India Hackathon 2023 - Plant Pharmers Team")
print("="*70)

try:
    loader = get_model_loader()
    print("\n✓ System ready!")
    print(f"✓ {len(loader.models)} models loaded")
    print(f"✓ {len(loader.class_names)} plant classes")
    print("\nStarting server...")
    print("="*70)
except Exception as e:
    print(f"\n✗ Error loading models: {str(e)}")
    print("Please make sure models are in the 'models/' folder")
    exit(1)

if __name__ == '__main__':
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )