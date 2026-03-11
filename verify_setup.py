#!/usr/bin/env python3
"""
Verification script to check if all packages are installed correctly
"""

import sys

print("=" * 50)
print("MEDICINAL PLANTS PROJECT - SETUP VERIFICATION")
print("=" * 50)
print()

# Check Python version
print(f"Python version: {sys.version}")
py_version = sys.version_info
if py_version.major == 3 and py_version.minor >= 9:
    print("✓ Python version is compatible (3.9+)")
else:
    print("✗ Python version is too old. Need 3.9+")
    sys.exit(1)

print()

# Check required packages
packages_to_check = [
    ('tensorflow', 'TensorFlow'),
    ('cv2', 'OpenCV'),
    ('numpy', 'NumPy'),
    ('pandas', 'Pandas'),
    ('sklearn', 'Scikit-learn'),
    ('matplotlib', 'Matplotlib'),
    ('seaborn', 'Seaborn'),
    ('flask', 'Flask'),
    ('PIL', 'Pillow'),
]

all_installed = True

for package_name, display_name in packages_to_check:
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {display_name}: {version}")
    except ImportError:
        print(f"✗ {display_name}: NOT INSTALLED")
        all_installed = False

print()
print("=" * 50)

if all_installed:
    print("🎉 SUCCESS! All packages installed correctly.")
    print()
    print("Next Steps:")
    print("1. Start collecting your dataset")
    print("2. Run the quick prototype script")
    print("3. Begin data preprocessing")
else:
    print("⚠ Some packages are missing.")
    print("Run: pip install -r requirements.txt")

print("=" * 50)