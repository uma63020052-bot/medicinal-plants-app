"""
STEP 4: Data Augmentation
Multiply your dataset 4-5x using image transformations

Creates variations of each image:
- Rotations
- Flips
- Brightness adjustments
- Zooms
- Shifts

USAGE:
python augment_dataset.py
"""

import os
import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from tqdm import tqdm
import random

# Configuration
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/augmented"
AUGMENTATIONS_PER_IMAGE = 4  # Create 4 variations of each image
TARGET_SIZE = (224, 224)

# Augmentation parameters
AUGMENTATION_CONFIG = {
    'rotation_range': 20,           # Rotate up to 20 degrees
    'width_shift_range': 0.1,       # Shift horizontally by 10%
    'height_shift_range': 0.1,      # Shift vertically by 10%
    'shear_range': 0.1,             # Shear transformation
    'zoom_range': 0.1,              # Zoom in/out by 10%
    'horizontal_flip': True,        # Random horizontal flip
    'brightness_range': [0.8, 1.2], # Brightness variation
    'fill_mode': 'nearest'          # Fill missing pixels with nearest value
}

def create_output_directories(input_dir, output_dir):
    """Create output directory structure"""
    print("Creating output directories...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all class folders
    class_folders = [f for f in os.listdir(input_dir) 
                     if os.path.isdir(os.path.join(input_dir, f))]
    
    # Create matching output folders
    for class_name in class_folders:
        class_output_path = os.path.join(output_dir, class_name)
        if not os.path.exists(class_output_path):
            os.makedirs(class_output_path)
    
    print(f"✓ Created {len(class_folders)} class directories")
    return class_folders

def augment_image(image_path, output_dir, num_augmentations, datagen):
    """
    Create augmented versions of a single image
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save augmented images
        num_augmentations: Number of variations to create
        datagen: ImageDataGenerator instance
    
    Returns:
        Number of images created
    """
    try:
        # Load image
        img = load_img(image_path, target_size=TARGET_SIZE)
        x = img_to_array(img)
        x = x.reshape((1,) + x.shape)  # Reshape to (1, height, width, channels)
        
        # Get base filename
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Generate augmented images
        i = 0
        for batch in datagen.flow(x, batch_size=1):
            # Convert to image
            augmented_img = batch[0].astype('uint8')
            
            # Save augmented image
            output_path = os.path.join(output_dir, f"{base_name}_aug{i}.jpg")
            cv2.imwrite(output_path, cv2.cvtColor(augmented_img, cv2.COLOR_RGB2BGR))
            
            i += 1
            if i >= num_augmentations:
                break
        
        return num_augmentations
    
    except Exception as e:
        print(f"Error augmenting {image_path}: {str(e)}")
        return 0

def augment_dataset(input_dir, output_dir, augmentations_per_image):
    """Augment entire dataset"""
    
    print("\n" + "=" * 70)
    print("DATA AUGMENTATION PIPELINE")
    print("=" * 70)
    
    # Create output directories
    class_folders = create_output_directories(input_dir, output_dir)
    
    # Count total images
    total_images = 0
    for class_name in class_folders:
        class_path = os.path.join(input_dir, class_name)
        images = [f for f in os.listdir(class_path)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        total_images += len(images)
    
    # Calculate expected output
    expected_output = total_images * (1 + augmentations_per_image)
    
    print(f"\nDataset Statistics:")
    print(f"  Classes: {len(class_folders)}")
    print(f"  Input Images: {total_images}")
    print(f"  Augmentations per Image: {augmentations_per_image}")
    print(f"  Expected Output: {expected_output} images")
    
    print(f"\nAugmentation Settings:")
    print(f"  Rotation: ±20°")
    print(f"  Horizontal Flip: Yes")
    print(f"  Brightness: 80-120%")
    print(f"  Zoom: ±10%")
    print(f"  Shift: ±10%")
    
    # Estimate time
    seconds_per_image = 0.5
    estimated_minutes = (total_images * seconds_per_image) / 60
    print(f"\nEstimated Time: {estimated_minutes:.1f} minutes")
    
    input("\nPress Enter to start augmentation...")
    
    # Create data generator
    datagen = ImageDataGenerator(**AUGMENTATION_CONFIG)
    
    print("\nAugmenting images...")
    
    total_created = 0
    total_copied = 0
    
    # Process each class
    for class_name in tqdm(class_folders, desc="Classes"):
        class_input_path = os.path.join(input_dir, class_name)
        class_output_path = os.path.join(output_dir, class_name)
        
        # Get all images in this class
        image_files = [f for f in os.listdir(class_input_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        # Process each image
        for img_file in tqdm(image_files, desc=f"  {class_name}", leave=False):
            input_path = os.path.join(class_input_path, img_file)
            
            # Copy original image to output
            img = cv2.imread(input_path)
            output_path = os.path.join(class_output_path, img_file)
            cv2.imwrite(output_path, img)
            total_copied += 1
            
            # Create augmented versions
            created = augment_image(
                input_path, 
                class_output_path, 
                augmentations_per_image,
                datagen
            )
            total_created += created
    
    # Summary
    total_output = total_copied + total_created
    
    print("\n" + "=" * 70)
    print("AUGMENTATION COMPLETE")
    print("=" * 70)
    print(f"✓ Original images copied: {total_copied}")
    print(f"✓ Augmented images created: {total_created}")
    print(f"✓ Total output images: {total_output}")
    print(f"✓ Multiplication factor: {total_output/total_images:.1f}x")
    
    print(f"\nAugmented dataset saved to: {output_dir}")
    
    print("\nNext Steps:")
    print("1. Run verify_augmented.py to check results")
    print("2. Preview augmentations with preview_augmentation.py")
    print("3. Proceed to model training (Step 5)")
    print("=" * 70)

def main():
    """Main function"""
    
    # Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        print("Please run preprocessing first (Step 3)")
        return
    
    # Start augmentation
    augment_dataset(INPUT_DIR, OUTPUT_DIR, AUGMENTATIONS_PER_IMAGE)

if __name__ == "__main__":
    main()