"""
Dataset Verification Script
Checks your medicinal plants dataset for completeness and quality

USAGE:
python verify_dataset.py
"""

import os
from PIL import Image
import cv2
from collections import defaultdict

# Configuration
DATA_DIR = "data/raw"
MIN_IMAGES_PER_CLASS = 50
MIN_IMAGE_SIZE = (224, 224)  # Minimum width x height in pixels

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def count_images_per_class(data_dir):
    """Count images in each class folder"""
    print_header("COUNTING IMAGES PER CLASS")
    
    class_stats = {}
    total_images = 0
    
    if not os.path.exists(data_dir):
        print_error(f"Data directory not found: {data_dir}")
        return {}, 0
    
    # Get all class folders
    class_folders = [f for f in os.listdir(data_dir) 
                     if os.path.isdir(os.path.join(data_dir, f))]
    
    if not class_folders:
        print_error(f"No class folders found in {data_dir}")
        return {}, 0
    
    # Count images in each class
    for class_name in sorted(class_folders):
        class_path = os.path.join(data_dir, class_name)
        
        # Count image files
        image_files = [f for f in os.listdir(class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        
        count = len(image_files)
        class_stats[class_name] = count
        total_images += count
        
        # Print status
        if count >= MIN_IMAGES_PER_CLASS:
            print_success(f"{class_name:.<40} {count:>4} images")
        elif count > 0:
            print_warning(f"{class_name:.<40} {count:>4} images (need {MIN_IMAGES_PER_CLASS - count} more)")
        else:
            print_error(f"{class_name:.<40} {count:>4} images (EMPTY)")
    
    return class_stats, total_images

def check_image_quality(data_dir, class_stats):
    """Check image quality (size, corruption, format)"""
    print_header("CHECKING IMAGE QUALITY")
    
    issues = {
        'too_small': [],
        'corrupted': [],
        'wrong_format': []
    }
    
    total_checked = 0
    
    for class_name, count in class_stats.items():
        class_path = os.path.join(data_dir, class_name)
        image_files = [f for f in os.listdir(class_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        
        print(f"\nChecking {class_name}... ({len(image_files)} images)")
        
        for img_file in image_files:
            img_path = os.path.join(class_path, img_file)
            total_checked += 1
            
            # Check if image can be opened
            try:
                img = Image.open(img_path)
                width, height = img.size
                
                # Check size
                if width < MIN_IMAGE_SIZE[0] or height < MIN_IMAGE_SIZE[1]:
                    issues['too_small'].append(f"{class_name}/{img_file} ({width}x{height})")
                
                # Check format
                if img.format not in ['JPEG', 'PNG', 'BMP', 'GIF']:
                    issues['wrong_format'].append(f"{class_name}/{img_file} ({img.format})")
                
                img.close()
                
            except Exception as e:
                issues['corrupted'].append(f"{class_name}/{img_file} - {str(e)}")
    
    # Report issues
    print(f"\n✓ Checked {total_checked} images")
    
    if issues['corrupted']:
        print_error(f"Found {len(issues['corrupted'])} corrupted images:")
        for img in issues['corrupted'][:10]:  # Show first 10
            print(f"  - {img}")
        if len(issues['corrupted']) > 10:
            print(f"  ... and {len(issues['corrupted']) - 10} more")
    
    if issues['too_small']:
        print_warning(f"Found {len(issues['too_small'])} images smaller than {MIN_IMAGE_SIZE}:")
        for img in issues['too_small'][:5]:  # Show first 5
            print(f"  - {img}")
        if len(issues['too_small']) > 5:
            print(f"  ... and {len(issues['too_small']) - 5} more")
    
    if issues['wrong_format']:
        print_warning(f"Found {len(issues['wrong_format'])} images in unusual formats:")
        for img in issues['wrong_format'][:5]:
            print(f"  - {img}")
    
    if not any(issues.values()):
        print_success("All images passed quality checks!")
    
    return issues

def generate_statistics(class_stats, total_images):
    """Generate dataset statistics"""
    print_header("DATASET STATISTICS")
    
    num_classes = len(class_stats)
    avg_images = total_images / num_classes if num_classes > 0 else 0
    
    min_class = min(class_stats, key=class_stats.get) if class_stats else None
    max_class = max(class_stats, key=class_stats.get) if class_stats else None
    
    classes_ready = sum(1 for count in class_stats.values() if count >= MIN_IMAGES_PER_CLASS)
    classes_need_more = sum(1 for count in class_stats.values() 
                           if 0 < count < MIN_IMAGES_PER_CLASS)
    classes_empty = sum(1 for count in class_stats.values() if count == 0)
    
    print(f"Total Classes: {num_classes}")
    print(f"Total Images: {total_images}")
    print(f"Average Images/Class: {avg_images:.1f}")
    
    if min_class:
        print(f"Smallest Class: {min_class} ({class_stats[min_class]} images)")
    if max_class:
        print(f"Largest Class: {max_class} ({class_stats[max_class]} images)")
    
    print(f"\nClass Readiness:")
    print(f"  ✓ Ready (≥{MIN_IMAGES_PER_CLASS} images): {classes_ready}")
    print(f"  ⚠ Need More (<{MIN_IMAGES_PER_CLASS} images): {classes_need_more}")
    print(f"  ✗ Empty: {classes_empty}")
    
    return {
        'num_classes': num_classes,
        'total_images': total_images,
        'avg_images': avg_images,
        'classes_ready': classes_ready,
        'classes_need_more': classes_need_more,
        'classes_empty': classes_empty
    }

def provide_recommendations(stats, issues):
    """Provide recommendations based on verification results"""
    print_header("RECOMMENDATIONS")
    
    recommendations = []
    
    # Check if dataset is large enough
    if stats['num_classes'] < 20:
        recommendations.append(
            f"⚠ You have {stats['num_classes']} classes. "
            f"Aim for at least 20 classes for initial prototype."
        )
    
    if stats['total_images'] < 1000:
        recommendations.append(
            f"⚠ You have {stats['total_images']} images. "
            f"Aim for at least 1000 images (20 classes × 50 images)."
        )
    
    # Check class balance
    if stats['classes_need_more'] > 0:
        recommendations.append(
            f"⚠ {stats['classes_need_more']} classes need more images. "
            f"Download more images for these classes."
        )
    
    if stats['classes_empty'] > 0:
        recommendations.append(
            f"✗ {stats['classes_empty']} classes are empty. "
            f"Remove these folders or add images."
        )
    
    # Check image quality issues
    if issues['corrupted']:
        recommendations.append(
            f"✗ Delete {len(issues['corrupted'])} corrupted images."
        )
    
    if issues['too_small']:
        recommendations.append(
            f"⚠ {len(issues['too_small'])} images are too small. "
            f"Consider removing or replacing them."
        )
    
    # Positive feedback
    if stats['classes_ready'] >= 20 and not any(issues.values()):
        recommendations.append(
            "✓ EXCELLENT! Your dataset is ready for preprocessing!"
        )
    elif stats['classes_ready'] >= 10:
        recommendations.append(
            "✓ GOOD PROGRESS! You can start with a smaller prototype."
        )
    
    # Print recommendations
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("No specific recommendations. Keep going!")
    
    print("\nNext Steps:")
    if stats['classes_ready'] >= 20:
        print("1. ✓ Proceed to data preprocessing (Step 3)")
        print("2. Run data augmentation")
        print("3. Train quick prototype model")
    else:
        print("1. Download more images for classes with <50 images")
        print("2. Add more plant classes if you have <20")
        print("3. Re-run this verification script")

def save_report(class_stats, stats, issues):
    """Save verification report to file"""
    report_file = "dataset_verification_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("MEDICINAL PLANTS DATASET VERIFICATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("DATASET STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Classes: {stats['num_classes']}\n")
        f.write(f"Total Images: {stats['total_images']}\n")
        f.write(f"Average Images/Class: {stats['avg_images']:.1f}\n")
        f.write(f"Classes Ready: {stats['classes_ready']}\n")
        f.write(f"Classes Need More: {stats['classes_need_more']}\n")
        f.write(f"Classes Empty: {stats['classes_empty']}\n\n")
        
        f.write("IMAGES PER CLASS\n")
        f.write("-" * 70 + "\n")
        for class_name, count in sorted(class_stats.items()):
            status = "✓" if count >= MIN_IMAGES_PER_CLASS else "⚠" if count > 0 else "✗"
            f.write(f"{status} {class_name:.<40} {count:>4} images\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    print(f"\n✓ Report saved to: {report_file}")

def main():
    """Main verification function"""
    print_header("MEDICINAL PLANTS DATASET VERIFICATION")
    
    # Step 1: Count images per class
    class_stats, total_images = count_images_per_class(DATA_DIR)
    
    if not class_stats:
        print("\n❌ No dataset found!")
        print(f"Please add images to: {DATA_DIR}")
        print("Organize as: data/raw/class_name/image_001.jpg")
        return
    
    # Step 2: Check image quality
    issues = check_image_quality(DATA_DIR, class_stats)
    
    # Step 3: Generate statistics
    stats = generate_statistics(class_stats, total_images)
    
    # Step 4: Provide recommendations
    provide_recommendations(stats, issues)
    
    # Step 5: Save report
    save_report(class_stats, stats, issues)
    
    print_header("VERIFICATION COMPLETE")

if __name__ == "__main__":
    main()