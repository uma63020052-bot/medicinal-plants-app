"""
Verify Processed Dataset
Checks if all images were processed correctly

USAGE:
python verify_processed.py
"""

import os
import cv2
import numpy as np
from collections import defaultdict

# Configuration
PROCESSED_DIR = "data/processed"
TARGET_SIZE = (224, 224)

def verify_processed_dataset(processed_dir, target_size):
    """Verify all processed images"""
    
    print("\n" + "=" * 70)
    print("PROCESSED DATASET VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(processed_dir):
        print(f"\n✗ Error: {processed_dir} not found!")
        print("Please run preprocessing first.")
        return
    
    # Get class folders
    class_folders = [f for f in os.listdir(processed_dir) 
                     if os.path.isdir(os.path.join(processed_dir, f))]
    
    if not class_folders:
        print(f"\n✗ No class folders found in {processed_dir}")
        return
    
    print(f"\nFound {len(class_folders)} classes")
    print(f"Expected size: {target_size}")
    print("\nChecking images...")
    
    # Statistics
    stats = {
        'total': 0,
        'correct_size': 0,
        'wrong_size': 0,
        'corrupted': 0
    }
    
    class_stats = {}
    wrong_size_examples = []
    
    # Check each class
    for class_name in sorted(class_folders):
        class_path = os.path.join(processed_dir, class_name)
        image_files = [f for f in os.listdir(class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        class_correct = 0
        class_wrong = 0
        class_corrupted = 0
        
        for img_file in image_files:
            img_path = os.path.join(class_path, img_file)
            stats['total'] += 1
            
            try:
                # Try to read image
                img = cv2.imread(img_path)
                
                if img is None:
                    stats['corrupted'] += 1
                    class_corrupted += 1
                    continue
                
                # Check size
                h, w = img.shape[:2]
                
                if (h, w) == target_size:
                    stats['correct_size'] += 1
                    class_correct += 1
                else:
                    stats['wrong_size'] += 1
                    class_wrong += 1
                    if len(wrong_size_examples) < 5:
                        wrong_size_examples.append(f"{class_name}/{img_file} ({w}x{h})")
            
            except Exception as e:
                stats['corrupted'] += 1
                class_corrupted += 1
        
        # Store class stats
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
    print(f"  Total Images: {stats['total']}")
    print(f"  ✓ Correct Size ({target_size}): {stats['correct_size']}")
    print(f"  ✗ Wrong Size: {stats['wrong_size']}")
    print(f"  ✗ Corrupted: {stats['corrupted']}")
    
    if stats['wrong_size'] > 0:
        print(f"\n⚠ Wrong Size Examples:")
        for example in wrong_size_examples:
            print(f"    {example}")
    
    print(f"\nPer-Class Statistics:")
    print("-" * 70)
    
    for class_name in sorted(class_stats.keys()):
        cs = class_stats[class_name]
        status = "✓" if cs['wrong'] == 0 and cs['corrupted'] == 0 else "✗"
        print(f"{status} {class_name:.<40} {cs['correct']}/{cs['total']} correct")
    
    # Final verdict
    print("\n" + "=" * 70)
    
    if stats['wrong_size'] == 0 and stats['corrupted'] == 0:
        print("✓ ALL IMAGES VERIFIED SUCCESSFULLY!")
        print("\nNext Steps:")
        print("1. Proceed to data augmentation (Step 4)")
        print("2. Train prototype model")
    else:
        print("⚠ SOME ISSUES FOUND")
        print("\nRecommendations:")
        if stats['corrupted'] > 0:
            print(f"  - {stats['corrupted']} corrupted images - delete and re-process")
        if stats['wrong_size'] > 0:
            print(f"  - {stats['wrong_size']} wrong size - re-run preprocessing")
    
    print("=" * 70)
    
    return stats

def compare_raw_vs_processed():
    """Compare image counts between raw and processed"""
    
    print("\n" + "=" * 70)
    print("COMPARING RAW vs PROCESSED")
    print("=" * 70)
    
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    
    if not os.path.exists(raw_dir):
        print(f"✗ Raw directory not found: {raw_dir}")
        return
    
    if not os.path.exists(processed_dir):
        print(f"✗ Processed directory not found: {processed_dir}")
        return
    
    # Count images in raw
    raw_classes = [f for f in os.listdir(raw_dir) 
                   if os.path.isdir(os.path.join(raw_dir, f))]
    
    raw_counts = {}
    for class_name in raw_classes:
        class_path = os.path.join(raw_dir, class_name)
        count = len([f for f in os.listdir(class_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        raw_counts[class_name] = count
    
    # Count images in processed
    processed_classes = [f for f in os.listdir(processed_dir) 
                        if os.path.isdir(os.path.join(processed_dir, f))]
    
    processed_counts = {}
    for class_name in processed_classes:
        class_path = os.path.join(processed_dir, class_name)
        count = len([f for f in os.listdir(class_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        processed_counts[class_name] = count
    
    # Compare
    print(f"\nRaw Classes: {len(raw_classes)}")
    print(f"Processed Classes: {len(processed_classes)}")
    
    all_classes = sorted(set(raw_classes) | set(processed_classes))
    
    print("\nClass-by-Class Comparison:")
    print("-" * 70)
    
    mismatches = 0
    
    for class_name in all_classes:
        raw_count = raw_counts.get(class_name, 0)
        proc_count = processed_counts.get(class_name, 0)
        
        if raw_count == proc_count:
            status = "✓"
        else:
            status = "✗"
            mismatches += 1
        
        print(f"{status} {class_name:.<40} Raw: {raw_count:>4}  Processed: {proc_count:>4}")
    
    print("-" * 70)
    print(f"Total Raw Images: {sum(raw_counts.values())}")
    print(f"Total Processed Images: {sum(processed_counts.values())}")
    
    if mismatches == 0:
        print("\n✓ All classes have matching image counts!")
    else:
        print(f"\n⚠ {mismatches} classes have mismatched counts")
        print("Some images may have failed during preprocessing")

def main():
    """Main function"""
    
    # Verify processed images
    stats = verify_processed_dataset(PROCESSED_DIR, TARGET_SIZE)
    
    # Compare with raw
    if stats:
        compare_raw_vs_processed()

if __name__ == "__main__":
    main()