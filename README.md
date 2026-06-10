# APASI — Aplikasi Pendeteksi Alam Sawit Indonesia

A deep learning-based oil palm fruit ripeness detection system, delivered as a Progressive Web App (PWA) with a FastAPI backend hosted on a VPS.

> **Model:** MobileNetV2 (Transfer Learning) — 89% accuracy, 14 MB  
> **Classes:** Belum Masak · Masak · Terlalu Masak · Bukan Sawit

---

## Repository Structure

```
apasi/
├── main.py                  # FastAPI backend — loads model, serves /predict endpoint
├── index.html               # PWA frontend — camera capture + prediction UI
├── manifest.json            # PWA manifest — enables "Add to Home Screen"
├── sw.js                    # Service Worker — offline caching
├── model_mobilenet.keras    # Trained MobileNetV2 model (do not delete)
└── .well-known/             # Domain verification files
```

---

## Requirements

### System
- Ubuntu 22.04+ (VPS) or Windows 11 (local)
- Python 3.10+
- 1 GB RAM minimum (2 GB recommended)

### Python Dependencies

```
fastapi
uvicorn
tensorflow-cpu       # use tensorflow if you have GPU
pillow
python-multipart
numpy
```

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Buriks420/apasi.git
cd apasi
```

### 2. Create a virtual environment

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn tensorflow-cpu pillow python-multipart numpy
```

> If you have a GPU, replace `tensorflow-cpu` with `tensorflow`

### 4. Verify the model file is present

```bash
ls model_mobilenet.keras
# Should output: model_mobilenet.keras
```

---

## Running the Backend

### Development (local)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (VPS)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

The API will be available at `http://your-server-ip:8000`

---

## API Endpoints

### `GET /`
Health check.

**Response:**
```json
{"status": "APASI API is running"}
```

---

### `POST /predict`
Submit an image for ripeness classification.

**Request:** `multipart/form-data` with field `file` (image)

**Response:**
```json
{
  "prediction": "Masak",
  "confidence": 0.89,
  "all_scores": {
    "Belum Masak": 0.05,
    "Masak": 0.89,
    "Terlalu Masak": 0.04,
    "Bukan Sawit": 0.02
  }
}
```

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@your_image.jpg"
```

**Test with Swagger UI:**  
Open `http://localhost:8000/docs` in your browser.

---

## Serving the Frontend (PWA)

The frontend (`index.html`) connects to the `/predict` endpoint. You need to serve it via a web server so the PWA features work correctly.

### Option A — Nginx (recommended for VPS)

```bash
sudo apt install nginx
```

Copy files to web root:
```bash
sudo cp index.html manifest.json sw.js /var/www/html/
```

Edit `/etc/nginx/sites-available/default` to proxy API calls:
```nginx
server {
    listen 80;

    location / {
        root /var/www/html;
        index index.html;
    }

    location /predict {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Option B — Quick local test

```bash
python3 -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

---

## Installing as a Mobile App (PWA)

1. Open the app URL in **Chrome on Android**
2. Tap the browser menu (⋮)
3. Select **"Add to Home Screen"**
4. The app installs like a native app — no Play Store needed

The camera input (`capture="environment"`) will open the **rear camera** automatically on mobile.

---

## Running on VPS (Production Checklist)

```bash
# 1. SSH into your VPS
ssh user@your-server-ip

# 2. Clone and install
git clone https://github.com/Buriks420/apasi.git
cd apasi
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn tensorflow-cpu pillow python-multipart numpy

# 3. Run with nohup so it stays alive after SSH disconnect
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &

# 4. Check it's running
curl http://localhost:8000/
```

To keep the server running permanently, use **systemd** or **screen**:
```bash
# Using screen
screen -S apasi
uvicorn main:app --host 0.0.0.0 --port 8000
# Press Ctrl+A then D to detach
```

---

## Model Details

| Model | Accuracy | Size | Notes |
|-------|----------|------|-------|
| Custom CNN | 60% | 45 MB | Baseline |
| ResNet50 | 44% | 98 MB | Overfitting on small dataset |
| **MobileNetV2** | **89%** | **14 MB** | ✅ Selected — best accuracy/size ratio |

Training was done on Google Colab (GPU). Dataset sourced from Kaggle via the Kaggle API.

---
