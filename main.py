from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = FastAPI(title="Sistem Deteksi Kelapa Sawit")

# Load your lightweight champion model
model = tf.keras.models.load_model('model_mobilenet.keras')

# The exact classes from your Colab training
CLASS_NAMES = ['Belum Masak', 'Bukan_Sawit', 'Masak', 'Terlalu Masak']

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/manifest.json")
def get_manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
def get_sw():
    return FileResponse("sw.js")

@app.get("/.well-known/assetlinks.json")
def get_assetlinks():
    return FileResponse(".well-known/assetlinks.json")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    # 1. Read the uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # 2. Resize it to the 224x224 that MobileNetV2 expects
    image = image.resize((224, 224))
    
    # 3. Convert to a tensor array and add a batch dimension
    img_array = tf.keras.preprocessing.image.img_to_array(image)
    img_array = tf.expand_dims(img_array, 0)
    
    # 4. Make the prediction!
    predictions = model.predict(img_array)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0]))
    
    # 5. Return the result as JSON
    return {
	"prediction": CLASS_NAMES[predicted_class_idx],
        "confidence": f"{round(confidence * 100, 2)}%"
    }
