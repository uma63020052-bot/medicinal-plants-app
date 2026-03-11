"""
Debug utilities for preprocessing pipeline
"""

import cv2
import numpy as np
import os
from datetime import datetime

def save_preprocessing_debug(original_path, preprocessed_image, output_dir='debug_output'):
    """
    Save both original and preprocessed images for debugging
    
    Args:
        original_path: Path to original uploaded image
        preprocessed_image: Preprocessed numpy array (with batch dimension)
        output_dir: Directory to save debug images
    
    Returns:
        dict with paths to saved images
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    
    # Read original
    original = cv2.imread(original_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    
    # Remove batch dimension and denormalize preprocessed image
    preprocessed_array = preprocessed_image[0]  # Remove batch dimension
    preprocessed_denorm = (preprocessed_array * 255).astype(np.uint8)
    
    # Save original
    original_save_path = os.path.join(output_dir, f'{timestamp}_{base_name}_1_original.jpg')
    cv2.imwrite(original_save_path, original)
    
    # Save preprocessed (convert RGB back to BGR for saving)
    preprocessed_bgr = cv2.cvtColor(preprocessed_denorm, cv2.COLOR_RGB2BGR)
    preprocessed_save_path = os.path.join(output_dir, f'{timestamp}_{base_name}_2_preprocessed.jpg')
    cv2.imwrite(preprocessed_save_path, preprocessed_bgr)
    
    # Create side-by-side comparison
    comparison = np.hstack([
        cv2.resize(original_rgb, (224, 224)),
        preprocessed_denorm
    ])
    comparison_bgr = cv2.cvtColor(comparison, cv2.COLOR_RGB2BGR)
    comparison_path = os.path.join(output_dir, f'{timestamp}_{base_name}_3_comparison.jpg')
    cv2.imwrite(comparison_path, comparison_bgr)
    
    return {
        'original': original_save_path,
        'preprocessed': preprocessed_save_path,
        'comparison': comparison_path,
        'timestamp': timestamp
    }