
import os
import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_PATH = r"c:/Users/mithracg/Downloads/agrisheild-final/plant_disease_model.h5"

def test_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}")
        return

    try:
        print("Loading model...")
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded.")

        img_array = np.zeros((224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        print("Predicting...")
        predictions = model.predict(img_array)
        print(f"Prediction shape: {predictions.shape}")
        print(f"Max confidence: {np.max(predictions)}")
        print(f"Predicted class index: {np.argmax(predictions)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
