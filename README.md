<div align="center">
  
  <img src="https://via.placeholder.com/800x200/000000/FFFFFF/?text=PhishDetect+Pro+Banner" alt="PhishDetect Pro Banner">

  <h1>🛡️ PhishDetect Pro</h1>
  
  <p><strong>A Hybrid Machine Learning & Rule-Based System for Phishing Detection</strong></p>

  ![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
  ![Django](https://img.shields.io/badge/Django-REST_API-092E20?style=for-the-badge&logo=django)
  ![Machine Learning](https://img.shields.io/badge/ML-XGBoost_%7C_Logistic_Regression-FF6F00?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)

</div>

---

## 📑 Table of Contents
- [About the Project](#-about-the-project)
- [System Architecture](#-system-architecture)
- [Visual Gallery (Deployment)](#-visual-gallery-deployment)
- [Performance Metrics](#-performance-metrics)
- [Installation & Setup](#-installation--setup)
- [API Documentation](#-api-documentation)

---

## 💡 About the Project

**PhishDetect Pro** bridges the gap between algorithmic accuracy and operational interpretability. While traditional machine learning models act as "black boxes," this framework combines probabilistic ML models with a deterministic rule-based heuristic engine to catch zero-day phishing attacks while explaining *exactly* why a threat was blocked.

### ✨ Key Features
* 🔍 **Dual-Vector Scanning:** Analyzes both URL structures and full email text payloads.
* 🧠 **Hybrid Ensemble:** Merges **XGBoost** (structured data) and **Logistic Regression** (TF-IDF text vectors).
* ⚡ **Low Latency:** Powered by a fast Django REST Framework (DRF) backend.
* 🌐 **Browser Extension:** Client-side Chrome extension for real-time user protection.
* 📊 **Admin Dashboard:** Centralized threat intelligence interface.

---

## 🏗️ System Architecture

> **Note:** The hybrid engine processes data concurrently. If the rule-based engine detects a known trusted domain, it can override the ML probability to prevent false positives.

1. **Preprocessing:** HTML stripping, token cleaning, and URL parsing.
2. **Feature Engineering:** Extracts structural metrics (length, IP presence) and semantic vectors (character/word-level TF-IDF).
3. **Ensemble Fusion:** A weighted algebraic scoring system synthesizes the probabilities into a final verdict.

---

## 📸 Visual Gallery (Deployment)

> **💡 How to add your images here:** Edit this README in GitHub, drag and drop your actual screenshots over the `src="..."` placeholder links below!

### 🛡️ 1. Chrome Extension (Real-Time Protection)

<div align="center">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Legitimate+URL+Extension+Image+Here" alt="Legitimate URL Extension" width="48%">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Phishing+URL+Extension+Image+Here" alt="Phishing URL Extension" width="48%">
</div>
<div align="center">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Legitimate+Email+Extension+Image+Here" alt="Legitimate Email Extension" width="48%">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Phishing+Email+Extension+Image+Here" alt="Phishing Email Extension" width="48%">
</div>

### 📊 2. Admin Web Dashboard

<div align="center">
  <img src="asstes/phishing url check.png" width="48%">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Phishing+URL+Dashboard+Image+Here" alt="Phishing URL Dashboard" width="48%">
</div>
<div align="center">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Legitimate+Email+Dashboard+Image+Here" alt="Legitimate Email Dashboard" width="48%">
  <img src="https://via.placeholder.com/600x300/e0e0e0/000000/?text=Drop+Phishing+Email+Dashboard+Image+Here" alt="Phishing Email Dashboard" width="48%">
</div>

---

## 📊 Performance Metrics

Evaluated on a strictly balanced, isolated test set (80/20 split) to prevent data leakage.

| Evaluation Target | Primary Model | Accuracy | ROC-AUC |
| :--- | :--- | :--- | :--- |
| **Malicious URLs** | XGBoost + Rules | `0.98` | **`0.9936`** |
| **Phishing Emails** | TF-IDF + LR + Rules | `0.98` | **`0.9987`** |

---

## 🚀 Installation & Setup

### 1. Backend Setup (Django API)
```bash
# Clone the repository
git clone [https://github.com/yourusername/PhishDetect-Pro.git](https://github.com/yourusername/PhishDetect-Pro.git)
cd PhishDetect-Pro/backend

# Create & activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies & run migrations
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# Start the server
python manage.py runserver

```

### 2. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`.
2. Toggle **Developer mode** (top right).
3. Click **Load unpacked** and select the `extension/` folder from this repo.

---

## 📡 API Documentation

**Endpoint:** `POST /api/v1/detect/`

<details>
<summary><b>Click to expand API Request/Response Example</b></summary>

**Request:**

```json
{
  "type": "url",
  "content": "[http://192.168.1.50/secure-update-paypal-verify/login](http://192.168.1.50/secure-update-paypal-verify/login)"
}

```

**Response:**

```json
{
  "status": "success",
  "classification": "Phishing",
  "final_score": 0.985,
  "ml_probability": 0.95,
  "rule_penalty": 0.35,
  "triggered_rules": [
    "Suspicious Keyword: 'paypal'",
    "Direct IP Address Detected",
    "Missing HTTPS Protocol"
  ],
  "interpretation": "Critical risk detected. Direct IP usage mimicking a financial institution."
}

```

</details>

---

<div align="center">
<p>Developed for the Master of Science in Cyber Security program at <b>Daffodil International University (DIU)</b>.</p>
</div>

```

```
