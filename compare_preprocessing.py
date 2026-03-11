"""
Before/After Comparison Viewer
Compare raw vs processed images side-by-side

USAGE:
python compare_preprocessing.py
"""

import os
import cv2
import numpy as np
import random

# Configuration
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def show_comparison(raw_dir, processed_dir, num_samples=5):
    """Show random before/after comparisons"""
    
    print("\n" + "=" * 70)
    print("BEFORE/AFTER PREPROCESSING COMPARISON")
    print("=" * 70)
    
    # Check directories exist
    if not os.path.exists(raw_dir):
        print(f"✗ Raw directory not found: {raw_dir}")
        return
    
    if not os.path.exists(processed_dir):
        print(f"✗ Processed directory not found: {processed_dir}")
        return
    
    # Get common classes
    raw_classes = set([f for f in os.listdir(raw_dir) 
                       if os.path.isdir(os.path.join(raw_dir, f))])
    processed_classes = set([f for f in os.listdir(processed_dir) 
                            if os.path.isdir(os.path.join(processed_dir, f))])
    
    common_classes = sorted(list(raw_classes & processed_classes))
    
    if not common_classes:
        print("✗ No common classes found between raw and processed!")
        return
    
    print(f"\nFound {len(common_classes)} classes")
    print(f"Showing {num_samples} random comparisons")
    print("\nControls:")
    print("  Press any key to see next comparison")
    print("  Press 'q' to quit")
    print("\nStarting viewer...")
    
    # Show random samples
    samples_shown = 0
    
    while samples_shown < num_samples:
        # Pick random class
        class_name = random.choice(common_classes)
        
        # Get images from this class
        raw_class_path = os.path.join(raw_dir, class_name)
        processed_class_path = os.path.join(processed_dir, class_name)
        
        raw_images = [f for f in os.listdir(raw_class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not raw_images:
            continue
        
        # Pick random image
        img_name = random.choice(raw_images)
        
        raw_img_path = os.path.join(raw_class_path, img_name)
        processed_img_path = os.path.join(processed_class_path, img_name)
        
        # Check if processed version exists
        if not os.path.exists(processed_img_path):
            continue
        
        try:
            # Load images
            raw_img = cv2.imread(raw_img_path)
            processed_img = cv2.imread(processed_img_path)
            
            if raw_img is None or processed_img is None:
                continue
            
            # Resize raw image for comparison (keep aspect ratio)
            h_raw, w_raw = raw_img.shape[:2]
            h_proc, w_proc = processed_img.shape[:2]
            
            # Resize raw to match processed height
            scale = h_proc / h_raw
            new_w = int(w_raw * scale)
            raw_resized = cv2.resize(raw_img, (new_w, h_proc))
            
            # Create side-by-side comparison
            gap = np.ones((h_proc, 20, 3), dtype=np.uint8) * 200
            comparison = np.hstack([raw_resized, gap, processed_img])
            
            # Add labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Black bar at top for text
            header = np.zeros((60, comparison.shape[1], 3), dtype=np.uint8)
            
            # Add text
            cv2.putText(header, f"Class: {class_name}", (10, 25), 
                       font, 0.7, (255, 255, 255), 2)
            cv2.putText(header, f"Image: {img_name}", (10, 50), 
                       font, 0.5, (200, 200, 200), 1)
            
            # Labels for before/after
            cv2.putText(comparison, "BEFORE", (20, 30), 
                       font, 1.0, (0, 0, 255), 2)
            cv2.putText(comparison, "AFTER", (raw_resized.shape[1] + 40, 30), 
                       font, 1.0, (0, 255, 0), 2)
            
            # Original size info
            cv2.putText(comparison, f"{w_raw}x{h_raw}", (20, 60), 
                       font, 0.5, (255, 255, 255), 1)
            cv2.putText(comparison, f"{w_proc}x{h_proc}", 
                       (raw_resized.shape[1] + 40, 60), 
                       font, 0.5, (255, 255, 255), 1)
            
            # Combine with header
            full_comparison = np.vstack([header, comparison])
            
            # Show
            cv2.imshow('Before/After Preprocessing', full_comparison)
            
            print(f"\nShowing: {class_name}/{img_name}")
            print(f"Sample {samples_shown + 1}/{num_samples}")
            
            # Wait for key press
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            
            samples_shown += 1
        
        except Exception as e:
            print(f"Error loading {class_name}/{img_name}: {str(e)}")
            continue
    
    cv2.destroyAllWindows()
    
    print("\n✓ Comparison viewer closed")
    print("=" * 70)

def show_grid_comparison(raw_dir, processed_dir):
    """Show 3x2 grid of before/after comparisons"""
    
    print("\n" + "=" * 70)
    print("GRID COMPARISON VIEWER")
    print("=" * 70)
    
    if not os.path.exists(raw_dir) or not os.path.exists(processed_dir):
        print("✗ Directories not found")
        return
    
    # Get classes
    raw_classes = [f for f in os.listdir(raw_dir) 
                   if os.path.isdir(os.path.join(raw_dir, f))]
    
    if not raw_classes:
        return
    
    print("\nControls:")
    print("  'n' - Next grid")
    print("  'q' - Quit")
    
    input("\nPress Enter to start...")
    
    while True:
        # Pick 3 random classes
        selected_classes = random.sample(raw_classes, min(3, len(raw_classes)))
        
        rows = []
        
        for class_name in selected_classes:
            raw_class_path = os.path.join(raw_dir, class_name)
            processed_class_path = os.path.join(processed_dir, class_name)
            
            # Get random image
            images = [f for f in os.listdir(raw_class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            if not images:
                continue
            
            img_name = random.choice(images)
            
            try:
                # Load images
                raw_img = cv2.imread(os.path.join(raw_class_path, img_name))
                proc_img = cv2.imread(os.path.join(processed_class_path, img_name))
                
                if raw_img is None or proc_img is None:
                    continue
                
                # Resize for grid
                raw_resized = cv2.resize(raw_img, (300, 300))
                proc_resized = cv2.resize(proc_img, (300, 300))
                
                # Add labels
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(raw_resized, "BEFORE", (10, 30), 
                           font, 0.7, (0, 0, 255), 2)
                cv2.putText(proc_resized, "AFTER", (10, 30), 
                           font, 0.7, (0, 255, 0), 2)
                
                cv2.putText(raw_resized, class_name[:15], (10, 290), 
                           font, 0.5, (255, 255, 255), 1)
                cv2.putText(proc_resized, class_name[:15], (10, 290), 
                           font, 0.5, (255, 255, 255), 1)
                
                # Combine horizontally
                gap = np.ones((300, 20, 3), dtype=np.uint8) * 200
                row = np.hstack([raw_resized, gap, proc_resized])
                rows.append(row)
            
            except:
                continue
        
        if not rows:
            print("No valid images found")
            break
        
        # Stack rows vertically
        gap_row = np.ones((20, rows[0].shape[1], 3), dtype=np.uint8) * 200
        grid = rows[0]
        for row in rows[1:]:
            grid = np.vstack([grid, gap_row, row])
        
        # Show
        cv2.imshow('Grid Comparison', grid)
        
        # Wait for key
        key = cv2.waitKey(0) & 0xFF
        
        if key == ord('q') or key == 27:
            break
    
    cv2.destroyAllWindows()
    print("\n✓ Grid viewer closed")

def main():
    """Main function"""
    
    print("\nChoose comparison mode:")
    print("1. Side-by-side (5 random samples)")
    print("2. Grid view (3x2 grid)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        show_comparison(RAW_DIR, PROCESSED_DIR, num_samples=5)
    elif choice == "2":
        show_grid_comparison(RAW_DIR, PROCESSED_DIR)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()