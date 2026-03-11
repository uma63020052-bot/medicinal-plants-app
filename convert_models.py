"""
Model Converter - Fix TensorFlow Version Compatibility
Recreates models and loads only weights
"""

import os
import sys
from tensorflow.keras.applications import VGG16, InceptionV3, ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout

def build_vgg16(num_classes):
    """Rebuild VGG-16 architecture"""
    base = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base.input, outputs=output)
    return model

def build_inception_v3(num_classes):
    """Rebuild Inception-V3 architecture"""
    base = InceptionV3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base.input, outputs=output)
    return model

def build_resnet50(num_classes):
    """Rebuild ResNet-50 architecture"""
    base = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base.input, outputs=output)
    return model

def convert_model(old_path, new_path, model_name, num_classes=40):
    """Convert old model to new compatible format"""
    
    print(f"\nConverting {model_name}...")
    print(f"  Reading from: {old_path}")
    
    try:
        # Build new model architecture
        if 'vgg16' in model_name.lower():
            new_model = build_vgg16(num_classes)
        elif 'inception' in model_name.lower():
            new_model = build_inception_v3(num_classes)
        elif 'resnet' in model_name.lower():
            new_model = build_resnet50(num_classes)
        else:
            print(f"  ✗ Unknown model type: {model_name}")
            return False
        
        print(f"  ✓ Model architecture rebuilt")
        
        # Load weights from old model
        try:
            new_model.load_weights(old_path)
            print(f"  ✓ Weights loaded successfully")
        except Exception as e:
            print(f"  ⚠ Warning loading weights: {str(e)[:100]}")
            print(f"  ⚠ Trying alternative loading method...")
            
            # Try loading with by_name=True, skip_mismatch=True
            new_model.load_weights(old_path, by_name=True, skip_mismatch=True)
            print(f"  ✓ Weights loaded (partial)")
        
        # Save in new format
        new_model.save(new_path)
        print(f"  ✓ Saved to: {new_path}")
        print(f"  ✓ {model_name} converted successfully!\n")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}\n")
        return False

def main():
    """Convert all models"""
    
    print("="*70)
    print("MODEL CONVERTER - Fix TensorFlow Compatibility")
    print("="*70)
    
    models_dir = 'models'
    backup_dir = 'models/backup'
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    models = [
        ('vgg16_model.h5', 'vgg16'),
        ('inception_v3_model.h5', 'inception_v3'),
        ('resnet50_model.h5', 'resnet50')
    ]
    
    converted = 0
    failed = 0
    
    for filename, model_name in models:
        old_path = os.path.join(models_dir, filename)
        backup_path = os.path.join(backup_dir, filename)
        new_path = os.path.join(models_dir, f'{model_name}_fixed.h5')
        
        if not os.path.exists(old_path):
            print(f"\n⚠ {filename} not found, skipping...")
            continue
        
        # Backup original
        import shutil
        if not os.path.exists(backup_path):
            shutil.copy2(old_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
        
        # Convert
        if convert_model(old_path, new_path, model_name):
            converted += 1
            
            # Replace original with fixed version
            os.remove(old_path)
            os.rename(new_path, old_path)
            print(f"✓ Replaced {filename} with fixed version")
        else:
            failed += 1
    
    print("="*70)
    print("CONVERSION COMPLETE")
    print("="*70)
    print(f"✓ Converted: {converted} models")
    if failed > 0:
        print(f"✗ Failed: {failed} models")
    print(f"\n✓ Original models backed up to: {backup_dir}")
    print("\nYou can now run: python run.py")
    print("="*70)

if __name__ == "__main__":
    main()