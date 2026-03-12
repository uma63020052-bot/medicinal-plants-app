"""
Model Loader
Loads Inception-V3 model with mobile-optimized preprocessing
"""

import os
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import cv2

import urllib.request

def download_models_if_needed(models_dir='models'):
    """Download models from HuggingFace if not present (for Render deployment)."""
    os.makedirs(models_dir, exist_ok=True)
    base_url = "https://huggingface.co/uma63020052/medicinal-plants-models/resolve/main"
    files = [
        "inception_v3_model.h5",
        "class_names.json"
    ]
    for filename in files:
        path = os.path.join(models_dir, filename)
        if not os.path.exists(path):
            print(f"⬇ Downloading {filename} from HuggingFace...")
            try:
                urllib.request.urlretrieve(f"{base_url}/{filename}?download=true", path)
                print(f"✓ Downloaded {filename}")
            except Exception as e:
                print(f"✗ Failed to download {filename}: {e}")

download_models_if_needed()


class ModelLoader:
    """Loads and manages the trained Inception-V3 model"""

    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.models = {}
        self.class_names = []
        self.load_models()
        self.load_class_names()

    def load_models(self):
        """Load Inception-V3 (and optionally other models if present)"""
        print("Loading models...")

        model_files = {
            'inception_v3': 'inception_v3_model.h5',
        }

        for name, filename in model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            if not os.path.exists(model_path):
                print(f"⚠  {name} not found at {model_path} — skipping")
                continue

            try:
                import tensorflow as tf
                self.models[name] = tf.keras.models.load_model(
                    model_path, compile=False, safe_mode=False
                )
                print(f"✓ {name} loaded")
            except Exception as e:
                try:
                    self.models[name] = load_model(model_path, compile=False)
                    print(f"✓ {name} loaded (fallback)")
                except Exception as e2:
                    print(f"✗ Could not load {name}: {str(e2)[:100]}")

        if not self.models:
            print("⚠ No models loaded - running in fallback mode")
            return

        print(f"✓ {len(self.models)} model(s) loaded: {list(self.models.keys())}")

    def load_class_names(self):
        """Load class names from JSON"""
        path = os.path.join(self.models_dir, 'class_names.json')
        if not os.path.exists(path):
            print(f"⚠ class_names.json not found at {path}")
            return
        with open(path, 'r') as f:
            self.class_names = json.load(f)
        print(f"✓ {len(self.class_names)} plant classes loaded")

    # ── Image preprocessing ──────────────────────────────────────────────────

    def preprocess_image(self, img_path, target_size=(224, 224), apply_preprocessing=True):
        """
        Full preprocessing pipeline matching training:
          1. Downscale large images first (handles 4K phone photos)
          2. CLAHE contrast enhancement
          3. Bilateral filter (noise reduction, preserves edges)
          4. GrabCut background removal (resized to ≤600px for speed)
          5. Resize to target_size
          6. Normalize to [0, 1]
        """
        print(f"  → Reading image...")
        img = cv2.imread(img_path)
        if img is None:
            raise Exception(f"Failed to read image: {img_path}")

        h, w = img.shape[:2]
        print(f"  → Original size: {w}x{h}")

        # Convert BGR → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if apply_preprocessing:
            # ── Step 1: Downscale large images to max 800px ─────────────────
            # Phone cameras produce 4000+ px images — shrink before processing
            max_dim = 800
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                print(f"  → Downscaled to {new_w}x{new_h}")

            # ── Step 2: CLAHE contrast enhancement ──────────────────────────
            img = self._apply_clahe(img)
            print(f"  → CLAHE applied")

            # ── Step 3: Bilateral filter (denoise, preserve edges) ───────────
            img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
            print(f"  → Bilateral filter applied")

            # ── Step 4: GrabCut background removal ──────────────────────────
            img = self._remove_background(img)
            print(f"  → Background removed")

        # ── Step 5: Resize to model input size ──────────────────────────────
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)
        print(f"  → Resized to {target_size}")

        # ── Step 6: Normalize to [0, 1] ─────────────────────────────────────
        img = img.astype('float32') / 255.0

        # ── Step 7: Add batch dimension ─────────────────────────────────────
        img = np.expand_dims(img, axis=0)
        print(f"  → Preprocessing complete ✓")

        return img

    def _apply_clahe(self, img_rgb):
        """Apply CLAHE contrast enhancement in LAB colour space"""
        try:
            lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            enhanced_lab = cv2.merge([l_enhanced, a, b])
            return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        except Exception as e:
            print(f"  ⚠  CLAHE failed ({str(e)[:40]}), skipping")
            return img_rgb

    def _remove_background(self, img_rgb):
        """
        GrabCut background removal.
        Expects image already downscaled to ≤800px.
        Falls back gracefully if it fails.
        """
        try:
            h, w = img_rgb.shape[:2]

            # Convert to BGR for GrabCut (OpenCV expects BGR)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            mask = np.zeros((h, w), np.uint8)

            # Use 10% margin on each side for the GrabCut rectangle
            margin_h = max(10, int(h * 0.10))
            margin_w = max(10, int(w * 0.10))
            rect = (margin_w, margin_h,
                    w - 2 * margin_w,
                    h - 2 * margin_h)

            if rect[2] <= 0 or rect[3] <= 0:
                print(f"  ⚠  Invalid GrabCut rect, skipping")
                return img_rgb

            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)

            # 3 iterations — good balance of speed vs quality
            cv2.grabCut(img_bgr, mask, rect, bgd_model, fgd_model, 3,
                        cv2.GC_INIT_WITH_RECT)

            # Foreground mask (GC_FGD=1, GC_PR_FGD=3)
            fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
                               1, 0).astype('uint8')

            # Morphological cleanup — remove tiny holes / noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN,  kernel)

            # Apply mask — white background for removed areas
            fg_mask_3ch = fg_mask[:, :, np.newaxis]
            result = img_rgb * fg_mask_3ch + (1 - fg_mask_3ch) * 255

            return result.astype('uint8')

        except Exception as e:
            print(f"  ⚠  GrabCut failed ({str(e)[:50]}), using original")
            return img_rgb

    def _simple_preprocess(self, img_path, target_size=(224, 224)):
        """Minimal preprocessing — resize + normalize only"""
        try:
            img = cv2.imread(img_path)
            if img is None:
                raise Exception("Failed to read image")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)
            img = img.astype('float32') / 255.0
            return np.expand_dims(img, axis=0)
        except Exception as e:
            raise Exception(f"Simple preprocessing error: {str(e)}")

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict(self, img_path, apply_preprocessing=True, debug=False):
        """
        Run prediction and return ensemble + per-model results.

        Priority:
          - If inception_v3 is loaded, its result is used as the primary signal.
          - If multiple models are loaded, probabilities are averaged (ensemble).
        """
        # Preprocess
        if apply_preprocessing:
            processed_img = self.preprocess_image(
                img_path, target_size=(224, 224),
                apply_preprocessing=True
            )
        else:
            processed_img = self._simple_preprocess(img_path)

        # Debug: save images
        if debug:
            try:
                from app.debug_utils import save_preprocessing_debug
                debug_paths = save_preprocessing_debug(img_path, processed_img)
                print(f"  Debug images saved: {debug_paths}")
            except Exception:
                debug_paths = {}

        # ── Run each model ───────────────────────────────────────────────────
        predictions   = {}
        all_probs     = []
        inception_probs = None

        for model_name, model in self.models.items():
            try:
                probs     = model.predict(processed_img, verbose=0)[0]
                top_idx   = int(np.argmax(probs))
                top_prob  = float(probs[top_idx])
                top_class = self.class_names[top_idx]

                # Top-5 for debugging
                top_5_idx = np.argsort(probs)[-5:][::-1]
                top_5 = [
                    {
                        'plant':      self.class_names[i],
                        'confidence': float(probs[i]),
                        'percentage': f"{probs[i] * 100:.2f}%"
                    }
                    for i in top_5_idx
                ]

                predictions[model_name] = {
                    'plant':      top_class,
                    'confidence': top_prob,
                    'percentage': f"{top_prob * 100:.2f}%",
                    'top_5':      top_5 if debug else None
                }

                all_probs.append(probs)

                if model_name == 'inception_v3':
                    inception_probs = probs

                print(f"  [{model_name}] → {top_class} ({top_prob * 100:.2f}%)")

            except Exception as e:
                print(f"  ✗ {model_name} prediction error: {str(e)}")
                predictions[model_name] = {'error': str(e)}

        # ── Ensemble ─────────────────────────────────────────────────────────
        if not all_probs:
            return {'ensemble': {'error': 'All models failed'}, 'individual_models': predictions}

        if len(all_probs) == 1:
            # Only one model — use directly
            ensemble_probs = all_probs[0]
        elif inception_probs is not None:
            # Inception-V3 weighted 2x; others 1x each
            weights = []
            for name in self.models.keys():
                if name in predictions and 'error' not in predictions[name]:
                    weights.append(2.0 if name == 'inception_v3' else 1.0)
            weight_arr = np.array(weights)
            weight_arr = weight_arr / weight_arr.sum()
            ensemble_probs = sum(w * p for w, p in zip(weight_arr, all_probs))
        else:
            # Simple average
            ensemble_probs = np.mean(all_probs, axis=0)

        ensemble_idx   = int(np.argmax(ensemble_probs))
        ensemble_prob  = float(ensemble_probs[ensemble_idx])
        ensemble_class = self.class_names[ensemble_idx]

        # Top-3
        top_3_idx = np.argsort(ensemble_probs)[-3:][::-1]
        top_3 = [
            {
                'plant':      self.class_names[i],
                'confidence': float(ensemble_probs[i]),
                'percentage': f"{ensemble_probs[i] * 100:.2f}%"
            }
            for i in top_3_idx
        ]

        if debug:
            top_10_idx = np.argsort(ensemble_probs)[-10:][::-1]
            print("\n  Top 10:")
            for rank, i in enumerate(top_10_idx, 1):
                print(f"    {rank}. {self.class_names[i]}: {ensemble_probs[i]*100:.2f}%")

        result = {
            'ensemble': {
                'plant':      ensemble_class,
                'confidence': ensemble_prob,
                'percentage': f"{ensemble_prob * 100:.2f}%",
                'top_3':      top_3,
            },
            'individual_models':    predictions,
            'preprocessing_applied': apply_preprocessing,
        }

        if debug:
            result['debug_images'] = debug_paths if 'debug_paths' in dir() else {}

        return result

    def get_model_info(self):
        return {
            'models_loaded': list(self.models.keys()),
            'num_models':    len(self.models),
            'num_classes':   len(self.class_names),
            'classes':       self.class_names,
        }


# ── Singleton ────────────────────────────────────────────────────────────────
_model_loader = None

def get_model_loader(models_dir='models'):
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader(models_dir)
    return _model_loader