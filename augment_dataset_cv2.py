"""
STEP 4: Data Augmentation (OpenCV Version - No TensorFlow needed)
Multiply your dataset 4-5x using image transformations

Uses only OpenCV and NumPy (already installed!)

USAGE:
python augment_dataset_cv2.py
"""

import os
import cv2
import numpy as np
from tqdm import tqdm
import random

# Configuration
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/augmented"
AUGMENTATIONS_PER_IMAGE = 4
TARGET_SIZE = (224, 224)

def rotate_image(image, angle):
    """Rotate image by given angle"""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # Get rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Rotate
    rotated = cv2.warpAffine(image, M, (w, h), 
                             borderMode=cv2.BORDER_REFLECT,
                             flags=cv2.INTER_LINEAR)
    
    return rotated

def flip_horizontal(image):
    """Flip image horizontally"""
    return cv2.flip(image, 1)

def adjust_brightness(image, factor):
    """Adjust image brightness"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = hsv[:, :, 2] * factor
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def zoom_image(image, zoom_factor):
    """Zoom in/out on image"""
    h, w = image.shape[:2]
    
    # Calculate new dimensions
    new_h = int(h * zoom_factor)
    new_w = int(w * zoom_factor)
    
    # Resize
    resized = cv2.resize(image, (new_w, new_h))
    
    if zoom_factor > 1:  # Zooming in - crop center
        start_h = (new_h - h) // 2
        start_w = (new_w - w) // 2
        result = resized[start_h:start_h+h, start_w:start_w+w]
    else:  # Zooming out - add padding
        result = np.ones((h, w, 3), dtype=np.uint8) * 255
        start_h = (h - new_h) // 2
        start_w = (w - new_w) // 2
        result[start_h:start_h+new_h, start_w:start_w+new_w] = resized
    
    return result

def shift_image(image, shift_x, shift_y):
    """Shift image by given pixels"""
    h, w = image.shape[:2]
    
    # Create translation matrix
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    
    # Shift
    shifted = cv2.warpAffine(image, M, (w, h),
                             borderMode=cv2.BORDER_REFLECT)
    
    return shifted

def create_augmentations(image):
    """Create 4 augmented versions of an image"""
    augmented = []
    
    # Augmentation 1: Rotation
    angle = random.uniform(-20, 20)
    aug1 = rotate_image(image, angle)
    augmented.append(aug1)
    
    # Augmentation 2: Horizontal flip + slight rotation
    aug2 = flip_horizontal(image)
    angle2 = random.uniform(-10, 10)
    aug2 = rotate_image(aug2, angle2)
    augmented.append(aug2)
    
    # Augmentation 3: Brightness adjustment
    brightness = random.uniform(0.8, 1.2)
    aug3 = adjust_brightness(image, brightness)
    augmented.append(aug3)
    
    # Augmentation 4: Zoom + shift
    zoom = random.uniform(0.9, 1.1)
    aug4 = zoom_image(image, zoom)
    shift_x = random.randint(-20, 20)
    shift_y = random.randint(-20, 20)
    aug4 = shift_image(aug4, shift_x, shift_y)
    augmented.append(aug4)
    
    return augmented

def augment_single_image(input_path, output_dir, num_augmentations):
    """Create augmented versions of a single image"""
    try:
        # Load image
        image = cv2.imread(input_path)
        
        if image is None:
            return 0
        
        # Get base filename
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # Create augmentations
        augmented_images = create_augmentations(image)
        
        # Save augmented images
        for i, aug_img in enumerate(augmented_images[:num_augmentations]):
            output_path = os.path.join(output_dir, f"{base_name}_aug{i}.jpg")
            cv2.imwrite(output_path, aug_img)
        
        return num_augmentations
    
    except Exception as e:
        print(f"Error augmenting {input_path}: {str(e)}")
        return 0

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

def augment_dataset(input_dir, output_dir, augmentations_per_image):
    """Augment entire dataset"""
    
    print("\n" + "=" * 70)
    print("DATA AUGMENTATION PIPELINE (OpenCV Version)")
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
    print(f"  Zoom: 90-110%")
    print(f"  Shift: ±20 pixels")
    
    # Estimate time
    seconds_per_image = 0.3  # OpenCV is faster
    estimated_minutes = (total_images * seconds_per_image) / 60
    print(f"\nEstimated Time: {estimated_minutes:.1f} minutes")
    
    input("\nPress Enter to start augmentation...")
    
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
            if img is not None:
                output_path = os.path.join(class_output_path, img_file)
                cv2.imwrite(output_path, img)
                total_copied += 1
                
                # Create augmented versions
                created = augment_single_image(
                    input_path, 
                    class_output_path, 
                    augmentations_per_image
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