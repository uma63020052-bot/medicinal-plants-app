"""
Quick Dataset Viewer (Fixed Version)
View samples from your medicinal plants dataset

USAGE:
python view_dataset.py

Press 'n' for next class, 'p' for previous, 'q' to quit
"""

import os
import cv2
import numpy as np
import random

# Configuration
DATA_DIR = "data/raw"
IMAGES_TO_SHOW = 6  # Show 6 images per class

def get_class_folders(data_dir):
    """Get list of class folders"""
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} not found!")
        return []
    
    folders = [f for f in os.listdir(data_dir) 
               if os.path.isdir(os.path.join(data_dir, f))]
    
    return sorted(folders)

def get_random_images(class_path, num_samples):
    """Get random image files from a class folder"""
    image_files = [f for f in os.listdir(class_path)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    if not image_files:
        return []
    
    # Sample randomly
    num_samples = min(num_samples, len(image_files))
    sampled_files = random.sample(image_files, num_samples)
    
    return [os.path.join(class_path, f) for f in sampled_files]

def create_grid_display(image_paths, class_name, class_info):
    """Create a grid of images with info overlay"""
    
    # Grid configuration
    rows, cols = 2, 3
    cell_size = 400  # Size of each cell
    
    # Create blank canvas
    canvas_width = cols * cell_size
    canvas_height = rows * cell_size + 100  # Extra space for header
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 240
    
    # Add header
    header_height = 80
    cv2.rectangle(canvas, (0, 0), (canvas_width, header_height), (50, 50, 50), -1)
    
    # Header text
    font = cv2.FONT_HERSHEY_SIMPLEX
    title = f"Class: {class_name.replace('_', ' ').title()}"
    cv2.putText(canvas, title, (20, 35), font, 1.0, (255, 255, 255), 2)
    cv2.putText(canvas, class_info, (20, 65), font, 0.6, (200, 200, 200), 1)
    
    # Load and display images in grid
    for idx, img_path in enumerate(image_paths):
        if idx >= rows * cols:
            break
        
        try:
            # Read image
            img = cv2.imread(img_path)
            if img is None:
                print(f"Could not load: {img_path}")
                continue
            
            # Calculate grid position
            row = idx // cols
            col = idx % cols
            
            # Resize image to fit cell
            img_resized = cv2.resize(img, (cell_size - 10, cell_size - 10))
            
            # Calculate position on canvas
            y_start = header_height + (row * cell_size) + 5
            x_start = (col * cell_size) + 5
            
            # Place image on canvas
            canvas[y_start:y_start + cell_size - 10, 
                   x_start:x_start + cell_size - 10] = img_resized
            
            # Draw border around image
            cv2.rectangle(canvas,
                         (x_start - 2, y_start - 2),
                         (x_start + cell_size - 12, y_start + cell_size - 12),
                         (100, 100, 100), 2)
        
        except Exception as e:
            print(f"Error loading {img_path}: {str(e)}")
            continue
    
    # Add footer with instructions
    footer_y = canvas_height - 20
    instructions = "Press: 'n' = Next | 'p' = Previous | 'r' = Refresh | 'q' = Quit"
    cv2.putText(canvas, instructions, (20, footer_y), 
                font, 0.6, (50, 50, 50), 1)
    
    return canvas

def view_dataset(data_dir):
    """Main viewer function"""
    
    # Get all class folders
    class_folders = get_class_folders(data_dir)
    
    if not class_folders:
        print("No classes found in dataset!")
        print(f"Make sure images are in: {data_dir}/class_name/")
        return
    
    print(f"\nFound {len(class_folders)} classes in dataset")
    print("\nKeyboard Controls:")
    print("  'n' - Next class")
    print("  'p' - Previous class")
    print("  'r' - Refresh (show different random images)")
    print("  'q' - Quit viewer")
    print("\nStarting viewer...\n")
    
    current_idx = 0
    window_name = 'Medicinal Plants Dataset Viewer'
    
    # Create window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    while True:
        class_name = class_folders[current_idx]
        class_path = os.path.join(data_dir, class_name)
        
        # Count total images in this class
        all_images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        num_total = len(all_images)
        
        if num_total == 0:
            print(f"No images found in {class_name}, skipping...")
            current_idx = (current_idx + 1) % len(class_folders)
            continue
        
        # Get random sample of images
        image_paths = get_random_images(class_path, IMAGES_TO_SHOW)
        
        # Create info string
        class_info = f"Images: {num_total} | Class {current_idx + 1}/{len(class_folders)}"
        
        # Create display
        print(f"Showing: {class_name} ({num_total} images)")
        display = create_grid_display(image_paths, class_name, class_info)
        
        # Show image
        cv2.imshow(window_name, display)
        
        # Wait for key press
        key = cv2.waitKey(0) & 0xFF
        
        if key == ord('n') or key == ord('N'):
            # Next class
            current_idx = (current_idx + 1) % len(class_folders)
            print("→ Next class")
            
        elif key == ord('p') or key == ord('P'):
            # Previous class
            current_idx = (current_idx - 1) % len(class_folders)
            print("← Previous class")
            
        elif key == ord('r') or key == ord('R'):
            # Refresh (show different random images from same class)
            print("↻ Refreshing images")
            
        elif key == ord('q') or key == ord('Q') or key == 27:  # 'q' or ESC
            # Quit
            print("\nClosing viewer...")
            break
        
        else:
            # Unknown key - show help
            print(f"Unknown key. Use: n=Next, p=Previous, r=Refresh, q=Quit")
    
    cv2.destroyAllWindows()
    print("Viewer closed.\n")

def print_summary(data_dir):
    """Print dataset summary"""
    class_folders = get_class_folders(data_dir)
    
    if not class_folders:
        return
    
    print("\n" + "=" * 65)
    print("DATASET SUMMARY")
    print("=" * 65)
    
    total_images = 0
    
    for idx, class_name in enumerate(class_folders, 1):
        class_path = os.path.join(data_dir, class_name)
        num_images = len([f for f in os.listdir(class_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        total_images += num_images
        print(f"{idx:2d}. {class_name:.<45} {num_images:>4} images")
    
    print("=" * 65)
    print(f"Total: {len(class_folders)} classes, {total_images:,} images")
    print("=" * 65)

def main():
    """Main function"""
    print("\n" + "=" * 65)
    print("   MEDICINAL PLANTS DATASET VIEWER")
    print("=" * 65)
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"\nError: Directory not found: {DATA_DIR}")
        print("Please make sure your images are organized as:")
        print(f"  {DATA_DIR}/class_name/image_001.jpg")
        return
    
    # Print summary
    print_summary(DATA_DIR)
    
    # Wait for user
    input("\nPress Enter to start the viewer...")
    
    # Start viewer
    try:
        view_dataset(DATA_DIR)
        print("\nThank you for using the dataset viewer!")
        
    except KeyboardInterrupt:
        print("\n\nViewer interrupted by user.")
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()