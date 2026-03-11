"""
STEP 3: Data Preprocessing Pipeline
Preprocesses all medicinal plant images for ML training

Features:
- Background removal
- Noise reduction
- Resizing to 224x224
- Normalization
- Progress tracking
- Error handling

USAGE:
python preprocess_images.py
"""

import os
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import shutil

# Configuration
INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
TARGET_SIZE = (224, 224)
REMOVE_BACKGROUND = True  # Set to False for faster processing
REMOVE_NOISE = True

def create_output_directories(input_dir, output_dir):
    """Create output directory structure matching input"""
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
    
    print(f"✓ Created {len(class_folders)} class directories in {output_dir}")
    return class_folders

def remove_background_grabcut(image):
    """
    Remove background using GrabCut algorithm
    Works well for leaves with distinct foreground
    """
    try:
        # Create mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Background & foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Define rectangle containing foreground (with 10px margin)
        h, w = image.shape[:2]
        rect = (10, 10, w - 20, h - 20)
        
        # Apply GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Create binary mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Apply mask to image
        result = image * mask2[:, :, np.newaxis]
        
        # Replace black background with white
        result[mask2 == 0] = [255, 255, 255]
        
        return result
    
    except Exception as e:
        # If GrabCut fails, return original image
        return image

def remove_background_simple(image):
    """
    Simple background removal using color thresholding
    Faster but less accurate than GrabCut
    """
    try:
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define range for green (leaf) color
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Morphological operations to clean mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Apply mask
        result = cv2.bitwise_and(image, image, mask=mask)
        
        # Replace black background with white
        result[mask == 0] = [255, 255, 255]
        
        return result
    
    except Exception as e:
        return image

def remove_noise(image):
    """Remove noise from image using Non-local Means Denoising"""
    try:
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        return denoised
    except Exception as e:
        return image

def resize_image(image, target_size):
    """Resize image to target size while maintaining aspect ratio"""
    try:
        # Get current dimensions
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate aspect ratio
        aspect = w / h
        
        if aspect > 1:  # Wide image
            new_w = target_w
            new_h = int(target_w / aspect)
        else:  # Tall image
            new_h = target_h
            new_w = int(target_h * aspect)
        
        # Resize
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Create white canvas
        canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 255
        
        # Calculate position to center the image
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        
        return canvas
    
    except Exception as e:
        # If resize fails, just do simple resize
        return cv2.resize(image, target_size)

def normalize_image(image):
    """Normalize pixel values to 0-1 range"""
    return image.astype(np.float32) / 255.0

def preprocess_single_image(input_path, output_path, remove_bg=True, denoise=True):
    """
    Preprocess a single image
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        remove_bg: Whether to remove background
        denoise: Whether to remove noise
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read image
        image = cv2.imread(input_path)
        
        if image is None:
            return False
        
        # Step 1: Remove background (optional)
        if remove_bg:
            image = remove_background_simple(image)
        
        # Step 2: Remove noise (optional)
        if denoise:
            image = remove_noise(image)
        
        # Step 3: Resize to target size
        image = resize_image(image, TARGET_SIZE)
        
        # Step 4: Save processed image
        cv2.imwrite(output_path, image)
        
        return True
    
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def preprocess_dataset(input_dir, output_dir, remove_bg=True, denoise=True):
    """
    Preprocess entire dataset
    
    Args:
        input_dir: Input directory (data/raw)
        output_dir: Output directory (data/processed)
        remove_bg: Whether to remove background
        denoise: Whether to remove noise
    """
    print("\n" + "=" * 70)
    print("MEDICINAL PLANTS - DATA PREPROCESSING PIPELINE")
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
    
    print(f"\nDataset Statistics:")
    print(f"  Classes: {len(class_folders)}")
    print(f"  Total Images: {total_images}")
    print(f"\nProcessing Settings:")
    print(f"  Target Size: {TARGET_SIZE}")
    print(f"  Remove Background: {remove_bg}")
    print(f"  Remove Noise: {denoise}")
    
    # Estimate processing time
    seconds_per_image = 2 if remove_bg else 0.5
    estimated_time = (total_images * seconds_per_image) / 60
    print(f"\nEstimated Time: {estimated_time:.1f} minutes")
    
    input("\nPress Enter to start preprocessing...")
    
    # Process all images
    print("\nProcessing images...")
    
    processed_count = 0
    failed_count = 0
    
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
            output_path = os.path.join(class_output_path, img_file)
            
            # Preprocess
            success = preprocess_single_image(input_path, output_path, remove_bg, denoise)
            
            if success:
                processed_count += 1
            else:
                failed_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("PREPROCESSING COMPLETE")
    print("=" * 70)
    print(f"✓ Successfully processed: {processed_count}/{total_images} images")
    
    if failed_count > 0:
        print(f"✗ Failed: {failed_count} images")
    
    print(f"\nProcessed images saved to: {output_dir}")
    print("\nNext Steps:")
    print("1. Run verify_processed.py to check processed images")
    print("2. Proceed to data augmentation (Step 4)")
    print("=" * 70)

def main():
    """Main function"""
    # Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        print("Please make sure your raw dataset is in data/raw/")
        return
    
    # Start preprocessing
    preprocess_dataset(
        INPUT_DIR, 
        OUTPUT_DIR,
        remove_bg=REMOVE_BACKGROUND,
        denoise=REMOVE_NOISE
    )

if __name__ == "__main__":
    main()