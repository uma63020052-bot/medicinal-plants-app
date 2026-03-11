"""
API Testing Script
Test your medicinal plant identification API
"""

import requests
import json
import os

API_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{API_URL}/api/health")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print("✓ Health check passed!")
        else:
            print("✗ Health check failed!")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("  Make sure the server is running: python run.py")

def test_info():
    """Test system info endpoint"""
    print("\n" + "="*70)
    print("TEST 2: System Information")
    print("="*70)
    
    try:
        response = requests.get(f"{API_URL}/api/info")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if data.get('success'):
            model_info = data['model_info']
            print(f"\n✓ API Version: {data['api_version']}")
            print(f"✓ Models Loaded: {model_info['models_loaded']}")
            print(f"✓ Number of Classes: {model_info['num_classes']}")
            print(f"✓ Sample Classes: {', '.join(model_info['classes'][:5])}...")
        else:
            print(f"✗ Failed: {data.get('error')}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_classes():
    """Test get classes endpoint"""
    print("\n" + "="*70)
    print("TEST 3: Get Plant Classes")
    print("="*70)
    
    try:
        response = requests.get(f"{API_URL}/api/classes")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if data.get('success'):
            print(f"\n✓ Total Classes: {data['count']}")
            print(f"✓ Classes: {', '.join(data['classes'][:10])}...")
        else:
            print(f"✗ Failed: {data.get('error')}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_prediction(image_path):
    """Test prediction endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Plant Prediction")
    print("="*70)
    
    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        print("  Please provide a valid image path")
        return
    
    try:
        print(f"Testing with: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/api/predict", files=files)
        
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if data.get('success'):
            ensemble = data['predictions']['ensemble']
            
            print(f"\n✓ Prediction: {ensemble['plant']}")
            print(f"✓ Confidence: {ensemble['percentage']}")
            print(f"✓ Processing Time: {data['processing_time']}")
            
            print("\nTop 3 Predictions:")
            for i, pred in enumerate(ensemble['top_3'], 1):
                print(f"  {i}. {pred['plant']} - {pred['percentage']}")
            
            print("\nIndividual Models:")
            for model, pred in data['predictions']['individual_models'].items():
                print(f"  {model}: {pred['plant']} - {pred['percentage']}")
        else:
            print(f"✗ Prediction failed: {data.get('error')}")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MEDICINAL PLANT API - TEST SUITE")
    print("="*70)
    
    # Test 1: Health Check
    test_health()
    
    # Test 2: System Info
    test_info()
    
    # Test 3: Get Classes
    test_classes()
    
    # Test 4: Prediction
    print("\n" + "="*70)
    print("PREDICTION TEST")
    print("="*70)
    
    # Try to find a test image
    test_image_paths = [
        "data/augmented/Tulasi/tulasi_001.jpg",
        "data/augmented/Aloevera/aloevera_001.jpg",
        "data/processed/Tulasi/tulasi_001.jpg",
    ]
    
    test_image = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if test_image:
        test_prediction(test_image)
    else:
        print("\n⚠ No test image found!")
        print("To test prediction, run:")
        print('  python test_api.py [path_to_image]')
        print("\nExample:")
        print('  python test_api.py data/augmented/Tulasi/tulasi_001.jpg')
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)
    
    print("\nIf all tests passed, your API is working perfectly! ✓")
    print("\nNext: Open http://localhost:5000 in your browser")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with provided image
        image_path = sys.argv[1]
        test_prediction(image_path)
    else:
        # Run full test suite
        main()