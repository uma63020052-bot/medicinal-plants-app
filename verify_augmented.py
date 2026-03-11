"""
Verify Augmented Dataset
Checks augmented dataset statistics and quality

USAGE:
python verify_augmented.py
"""

import os
import cv2
from collections import defaultdict

# Configuration
AUGMENTED_DIR = "data/augmented"
PROCESSED_DIR = "data/processed"
TARGET_SIZE = (224, 224)

def verify_augmented_dataset(augmented_dir, processed_dir):
    """Verify augmented dataset"""
    
    print("\n" + "=" * 70)
    print("AUGMENTED DATASET VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(augmented_dir):
        print(f"\n✗ Error: {augmented_dir} not found!")
        print("Please run augmentation first.")
        return
    
    # Get class folders
    aug_classes = sorted([f for f in os.listdir(augmented_dir) 
                          if os.path.isdir(os.path.join(augmented_dir, f))])
    
    if not aug_classes:
        print(f"\n✗ No class folders found in {augmented_dir}")
        return
    
    print(f"\nFound {len(aug_classes)} classes")
    print(f"Expected size: {TARGET_SIZE}")
    
    # Count images and check quality
    print("\nVerifying images...")
    
    class_stats = {}
    total_images = 0
    correct_size = 0
    wrong_size = 0
    corrupted = 0
    
    for class_name in aug_classes:
        class_path = os.path.join(augmented_dir, class_name)
        image_files = [f for f in os.listdir(class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        class_correct = 0
        class_wrong = 0
        class_corrupted = 0
        
        for img_file in image_files:
            img_path = os.path.join(class_path, img_file)
            total_images += 1
            
            try:
                img = cv2.imread(img_path)
                
                if img is None:
                    corrupted += 1
                    class_corrupted += 1
                    continue
                
                h, w = img.shape[:2]
                
                if (h, w) == TARGET_SIZE:
                    correct_size += 1
                    class_correct += 1
                else:
                    wrong_size += 1
                    class_wrong += 1
            
            except:
                corrupted += 1
                class_corrupted += 1
        
        class_stats[class_name] = {
            'total': len(image_files),
            'correct': class_correct,
            'wrong': class_wrong,
            'corrupted': class_corrupted
        }
    
    # Print results
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    print(f"\nOverall Statistics:")
    print(f"  Total Images: {total_images}")
    print(f"  ✓ Correct Size: {correct_size}")
    print(f"  ✗ Wrong Size: {wrong_size}")
    print(f"  ✗ Corrupted: {corrupted}")
    
    print(f"\nPer-Class Statistics:")
    print("-" * 70)
    
    for class_name in sorted(class_stats.keys()):
        cs = class_stats[class_name]
        status = "✓" if cs['wrong'] == 0 and cs['corrupted'] == 0 else "✗"
        print(f"{status} {class_name:.<40} {cs['total']:>5} images")
    
    # Compare with processed dataset
    if os.path.exists(processed_dir):
        print("\n" + "=" * 70)
        print("AUGMENTATION STATISTICS")
        print("=" * 70)
        
        # Count processed images
        proc_classes = [f for f in os.listdir(processed_dir) 
                       if os.path.isdir(os.path.join(processed_dir, f))]
        
        processed_total = 0
        for class_name in proc_classes:
            class_path = os.path.join(processed_dir, class_name)
            images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            processed_total += len(images)
        
        multiplication_factor = total_images / processed_total if processed_total > 0 else 0
        
        print(f"\nOriginal (Processed): {processed_total} images")
        print(f"Augmented: {total_images} images")
        print(f"Multiplication Factor: {multiplication_factor:.1f}x")
        
        # Show breakdown
        original_count = processed_total
        augmented_count = total_images - processed_total
        
        print(f"\nBreakdown:")
        print(f"  Original images: {original_count}")
        print(f"  Augmented images: {augmented_count}")
    
    # Final verdict
    print("\n" + "=" * 70)
    
    if wrong_size == 0 and corrupted == 0:
        print("✓ ALL IMAGES VERIFIED SUCCESSFULLY!")
        print("\nNext Steps:")
        print("1. Preview augmentations with preview_augmentation.py")
        print("2. Proceed to model training (Step 5)")
    else:
        print("⚠ SOME ISSUES FOUND")
        if corrupted > 0:
            print(f"  - {corrupted} corrupted images")
        if wrong_size > 0:
            print(f"  - {wrong_size} wrong size images")
    
    print("=" * 70)
    
    return class_stats

def main():
    """Main function"""
    verify_augmented_dataset(AUGMENTED_DIR, PROCESSED_DIR)

if __name__ == "__main__":
    main()