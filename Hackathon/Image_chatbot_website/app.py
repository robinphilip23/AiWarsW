
import os
import time
from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import requests
import json

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/scanner")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'plant_disease_model.h5')
print(f"Loading model from: {MODEL_PATH}")

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

CLASS_NAMES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 
    'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 
    'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 
    'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 
    'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 
    'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 
    'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 
    'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]


# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# API Configuration
# Load from environment variable (set in .env for local dev)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


def get_disease_details(disease_name):
    if not OPENROUTER_API_KEY:
        return {
            "description": "Description unavailable. Please provide an OpenRouter API Key in app.py to fetch details.",
            "treatments": ["<ul><li>Add API Key to app.py</li><li>Restart the application</li><li>Try again</li></ul>"]
        }

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Clean name for prompt
        clean_name = disease_name.replace("___", " ").replace("_", " ")
        
        prompt = f"""
        Act as an agricultural expert. Provide a short description and 3 specific treatment steps for the plant disease for small farmers: "{clean_name}".
        
        Format the output EXACTLY as this JSON:
        {{
            "description": "2-3 sentences explaining the disease.",
            "treatments": "<ul><li>Step 1</li><li>Step 2</li><li>Step 3</li></ul>"
        }}
        """

        data = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Simple cleanup if the model adds markdown code blocks
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        else:
            print(f"API Error: {response.text}")
            return {
                "description": "Could not fetch details from AI.",
                "treatments": "<ul><li>Check network connection</li><li>Verify API Key</li></ul>"
            }
            
    except Exception as e:
        print(f"LLM Error: {e}")
        return {
            "description": "Error connecting to knowledge base.",
            "treatments": "<ul><li>System Error</li></ul>"
        }

@app.route("/identify", methods=["POST"])
def identify():
    if model is None:
        return render_template("index.html", error="Model not loaded")
        
    image_file = request.files.get("image")
    
    if not image_file:
        return render_template("index.html", error="No image uploaded")

    try:
        # Save image for display
        filename = f"{int(time.time())}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        
        # Preprocess for model
        img = Image.open(filepath)
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = model.predict(img_array)
        confidence = float(np.max(predictions))
        class_idx = np.argmax(predictions)
        predicted_class = CLASS_NAMES[class_idx]
        
        # Formatting
        confidence_str = f"{confidence * 100:.2f}%"
        display_name = predicted_class.replace("___", ": ").replace("_", " ")
        
        # Fetch Details from LLM
        details = get_disease_details(predicted_class)
        
        # Return Result Page
        return render_template(
            "result.html",
            image_url=f"/static/uploads/{filename}",
            disease_name=display_name,
            confidence=confidence_str,
            description=details.get("description", "No description available."),
            treatments=details.get("treatments", "No treatments available.")
        )
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)