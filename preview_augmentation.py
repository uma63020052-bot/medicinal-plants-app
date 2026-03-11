"""
Preview Augmentations
View original image vs augmented versions side-by-side

USAGE:
python preview_augmentation.py
"""

import os
import cv2
import numpy as np
import random

# Configuration
PROCESSED_DIR = "data/processed"
AUGMENTED_DIR = "data/augmented"

def show_augmentation_preview(processed_dir, augmented_dir, num_samples=5):
    """Show original vs augmented images"""
    
    print("\n" + "=" * 70)
    print("AUGMENTATION PREVIEW")
    print("=" * 70)
    
    # Check directories
    if not os.path.exists(processed_dir):
        print(f"✗ Processed directory not found: {processed_dir}")
        return
    
    if not os.path.exists(augmented_dir):
        print(f"✗ Augmented directory not found: {augmented_dir}")
        return
    
    # Get classes
    classes = [f for f in os.listdir(processed_dir) 
               if os.path.isdir(os.path.join(processed_dir, f))]
    
    if not classes:
        print("✗ No classes found")
        return
    
    print(f"\nFound {len(classes)} classes")
    print(f"Showing {num_samples} random examples")
    print("\nControls:")
    print("  Press any key to see next example")
    print("  Press 'q' to quit")
    
    input("\nPress Enter to start...")
    
    samples_shown = 0
    
    while samples_shown < num_samples:
        # Pick random class
        class_name = random.choice(classes)
        
        # Get original images from processed
        proc_class_path = os.path.join(processed_dir, class_name)
        proc_images = [f for f in os.listdir(proc_class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
                      and not '_aug' in f]  # Only original images
        
        if not proc_images:
            continue
        
        # Pick random original image
        original_img_name = random.choice(proc_images)
        original_path = os.path.join(proc_class_path, original_img_name)
        
        # Get augmented versions of this image
        aug_class_path = os.path.join(augmented_dir, class_name)
        base_name = os.path.splitext(original_img_name)[0]
        
        aug_images = [f for f in os.listdir(aug_class_path)
                     if f.startswith(base_name) and '_aug' in f]
        
        if not aug_images or len(aug_images) < 4:
            continue
        
        try:
            # Load original image
            original = cv2.imread(original_path)
            if original is None:
                continue
            
            # Load up to 4 augmented versions
            augmented = []
            for aug_name in aug_images[:4]:
                aug_path = os.path.join(aug_class_path, aug_name)
                aug_img = cv2.imread(aug_path)
                if aug_img is not None:
                    augmented.append(aug_img)
            
            if len(augmented) < 4:
                continue
            
            # Create display grid: 1 original + 4 augmented = 5 images in row
            # Resize for display
            display_size = (200, 200)
            
            original_display = cv2.resize(original, display_size)
            augmented_display = [cv2.resize(aug, display_size) for aug in augmented]
            
            # Add labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Label original
            cv2.putText(original_display, "ORIGINAL", (10, 30), 
                       font, 0.6, (0, 255, 0), 2)
            
            # Label augmented
            for i, aug_disp in enumerate(augmented_display):
                cv2.putText(aug_disp, f"AUGMENTED {i+1}", (10, 30), 
                           font, 0.5, (0, 165, 255), 2)
            
            # Create row
            gap = np.ones((display_size[1], 10, 3), dtype=np.uint8) * 200
            row = original_display
            for aug_disp in augmented_display:
                row = np.hstack([row, gap, aug_disp])
            
            # Add header
            header_height = 60
            header = np.zeros((header_height, row.shape[1], 3), dtype=np.uint8)
            
            cv2.putText(header, f"Class: {class_name}", (10, 25), 
                       font, 0.8, (255, 255, 255), 2)
            cv2.putText(header, f"Image: {original_img_name}", (10, 50), 
                       font, 0.5, (200, 200, 200), 1)
            
            # Combine
            display = np.vstack([header, row])
            
            # Show
            cv2.imshow('Augmentation Preview', display)
            
            print(f"\nShowing: {class_name}/{original_img_name}")
            print(f"Sample {samples_shown + 1}/{num_samples}")
            
            # Wait for key
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('q') or key == 27:
                break
            
            samples_shown += 1
        
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    cv2.destroyAllWindows()
    print("\n✓ Preview closed")
    print("=" * 70)

def show_grid_comparison(processed_dir, augmented_dir):
    """Show 3x3 grid of augmented examples"""
    
    print("\n" + "=" * 70)
    print("AUGMENTATION GRID VIEW")
    print("=" * 70)
    
    if not os.path.exists(processed_dir) or not os.path.exists(augmented_dir):
        print("✗ Directories not found")
        return
    
    classes = [f for f in os.listdir(processed_dir) 
               if os.path.isdir(os.path.join(processed_dir, f))]
    
    if not classes:
        return
    
    print("\nControls:")
    print("  'n' - Next grid")
    print("  'q' - Quit")
    
    input("\nPress Enter to start...")
    
    while True:
        # Pick random class
        class_name = random.choice(classes)
        
        # Get an original image and its augmentations
        proc_class_path = os.path.join(processed_dir, class_name)
        aug_class_path = os.path.join(augmented_dir, class_name)
        
        proc_images = [f for f in os.listdir(proc_class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
                      and not '_aug' in f]
        
        if not proc_images:
            continue
        
        original_name = random.choice(proc_images)
        base_name = os.path.splitext(original_name)[0]
        
        # Get augmented versions
        aug_images = [f for f in os.listdir(aug_class_path)
                     if f.startswith(base_name)]
        
        if len(aug_images) < 9:
            continue
        
        try:
            # Load 9 images (1 original + 8 augmented)
            grid_images = []
            
            for img_name in aug_images[:9]:
                img_path = os.path.join(aug_class_path, img_name)
                img = cv2.imread(img_path)
                if img is not None:
                    img_resized = cv2.resize(img, (200, 200))
                    
                    # Add label
                    if '_aug' in img_name:
                        label = "Augmented"
                        color = (0, 165, 255)
                    else:
                        label = "Original"
                        color = (0, 255, 0)
                    
                    cv2.putText(img_resized, label, (10, 25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    grid_images.append(img_resized)
            
            if len(grid_images) < 9:
                continue
            
            # Create 3x3 grid
            gap = 10
            rows = []
            for i in range(3):
                row_imgs = grid_images[i*3:(i+1)*3]
                gap_col = np.ones((200, gap, 3), dtype=np.uint8) * 200
                row = row_imgs[0]
                for img in row_imgs[1:]:
                    row = np.hstack([row, gap_col, img])
                rows.append(row)
            
            gap_row = np.ones((gap, rows[0].shape[1], 3), dtype=np.uint8) * 200
            grid = rows[0]
            for row in rows[1:]:
                grid = np.vstack([grid, gap_row, row])
            
            # Add header
            header = np.zeros((50, grid.shape[1], 3), dtype=np.uint8)
            cv2.putText(header, f"Class: {class_name} - Augmentation Examples", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            display = np.vstack([header, grid])
            
            # Show
            cv2.imshow('Augmentation Grid', display)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('q') or key == 27:
                break
        
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    cv2.destroyAllWindows()
    print("\n✓ Grid viewer closed")

def main():
    """Main function"""
    
    print("\nChoose preview mode:")
    print("1. Side-by-side (1 original + 4 augmented)")
    print("2. Grid view (3x3 grid)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        show_augmentation_preview(PROCESSED_DIR, AUGMENTED_DIR, num_samples=5)
    elif choice == "2":
        show_grid_comparison(PROCESSED_DIR, AUGMENTED_DIR)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()