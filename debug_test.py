"""
Debug Test Script
Test predictions and see preprocessing results

USAGE:
python debug_test.py path/to/image.jpg
"""

import sys
import requests
import json

API_URL = "http://localhost:5000"

def test_with_preprocessing(image_path):
    """Test with full preprocessing pipeline"""
    print("\n" + "="*70)
    print("TEST 1: WITH PREPROCESSING")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'preprocess': 'true', 'debug': 'true'}
        response = requests.post(f"{API_URL}/api/predict", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Prediction: {result['predictions']['ensemble']['plant']}")
        print(f"✓ Confidence: {result['predictions']['ensemble']['percentage']}")
        print(f"✓ Processing time: {result['processing_time']}")
        
        print("\nTop 3 Predictions:")
        for i, pred in enumerate(result['predictions']['ensemble']['top_3'], 1):
            print(f"  {i}. {pred['plant']}: {pred['percentage']}")
        
        print("\nIndividual Models:")
        for model, pred in result['predictions']['individual_models'].items():
            print(f"  {model}: {pred['plant']} ({pred['percentage']})")
        
        if result.get('debug_mode'):
            print("\n✓ Debug images saved in debug_output/ folder")
            print("  Check comparison image to see preprocessing effect")
    else:
        print(f"✗ Error: {response.json()}")

def test_without_preprocessing(image_path):
    """Test without preprocessing (simple resize only)"""
    print("\n" + "="*70)
    print("TEST 2: WITHOUT PREPROCESSING (Simple resize only)")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'preprocess': 'false'}
        response = requests.post(f"{API_URL}/api/predict", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Prediction: {result['predictions']['ensemble']['plant']}")
        print(f"✓ Confidence: {result['predictions']['ensemble']['percentage']}")
        print(f"✓ Processing time: {result['processing_time']}")
        
        print("\nTop 3 Predictions:")
        for i, pred in enumerate(result['predictions']['ensemble']['top_3'], 1):
            print(f"  {i}. {pred['plant']}: {pred['percentage']}")
    else:
        print(f"✗ Error: {response.json()}")

def check_classes():
    """Check available plant classes"""
    print("\n" + "="*70)
    print("AVAILABLE PLANT CLASSES")
    print("="*70)
    
    response = requests.get(f"{API_URL}/api/classes")
    if response.status_code == 200:
        data = response.json()
        classes = data['classes']
        
        print(f"\nTotal classes: {len(classes)}")
        print("\nAll classes:")
        for i, plant in enumerate(classes, 1):
            print(f"  {i:2d}. {plant}")
        
        # Check if Tulasi exists
        if 'Tulasi' in classes:
            print(f"\n✓ 'Tulasi' found at position {classes.index('Tulasi') + 1}")
        else:
            print("\n⚠ 'Tulasi' not found in classes!")
            # Check for similar names
            tulasi_like = [c for c in classes if 'tul' in c.lower() or 'holy' in c.lower()]
            if tulasi_like:
                print(f"  Similar names found: {tulasi_like}")
        
        # Check if Insulin exists
        if 'Insulin' in classes:
            print(f"✓ 'Insulin' found at position {classes.index('Insulin') + 1}")
        else:
            print("✗ 'Insulin' not found in classes")
            # Check for similar
            insulin_like = [c for c in classes if 'ins' in c.lower()]
            if insulin_like:
                print(f"  Similar names found: {insulin_like}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_test.py path/to/image.jpg")
        print("\nExample:")
        print("  python debug_test.py data/augmented/Tulasi/tulasi_001.jpg")
        return
    
    image_path = sys.argv[1]
    
    print("\n" + "="*70)
    print("MEDICINAL PLANT PREDICTION - DEBUG TEST")
    print("="*70)
    print(f"Image: {image_path}")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/api/health")
        if response.status_code != 200:
            print("\n✗ Server not responding!")
            print("Please start server: python run.py")
            return
    except:
        print("\n✗ Cannot connect to server!")
        print("Please start server: python run.py")
        return
    
    # Check classes first
    check_classes()
    
    # Test with preprocessing
    test_with_preprocessing(image_path)
    
    # Test without preprocessing
    test_without_preprocessing(image_path)
    
    print("\n" + "="*70)
    print("DEBUGGING TIPS")
    print("="*70)
    print("\n1. Check debug_output/ folder for preprocessed images")
    print("2. Compare original vs preprocessed to see if preprocessing is too aggressive")
    print("3. If wrong prediction, try toggling preprocessing on/off")
    print("4. Check if class names match your training data")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()