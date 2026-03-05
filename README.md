# 🛡️ PhishDetect Pro

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-REST%20Framework-green)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-XGBoost%20%7C%20LR-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**PhishDetect Pro** is an advanced, real-time hybrid phishing detection framework designed to identify both malicious URLs and deceptive phishing emails. It bridges the gap between algorithmic accuracy and operational interpretability by combining probabilistic machine learning models with a deterministic rule-based heuristic engine.

This project was developed as a Master of Science in Cyber Security thesis at Daffodil International University (DIU).

---

## ✨ Key Features

* **Dual-Vector Detection:** Scans and classifies both URL strings and full email body texts.
* **Hybrid Ensemble Engine:** Combines **XGBoost** (for structured URL features) and **Logistic Regression** (for high-dimensional TF-IDF text features) with a strict rule-based penalty system.
* **Real-Time API:** Fully functional backend powered by Django REST Framework (DRF) for low-latency inference.
* **Chrome Browser Extension:** Client-side integration that actively monitors browsing traffic and provides instant visual threat warnings.
* **Admin Web Dashboard:** Centralized interface for security administrators to analyze threats, view risk scores, and understand the exact rules or keywords that triggered an alert.
* **Highly Interpretable:** Solves the ML "black box" problem by outputting exactly which heuristic rules or keywords contributed to a "Phishing" classification.

---

## 🏗️ System Architecture

The pipeline processes raw digital communications through a multi-stage architecture:

1.  **Preprocessing:** Normalization, HTML stripping, token cleaning, and URL parsing.
2.  **Feature Engineering:** * *Structural:* Length, dot counts, subdomain depth, IP presence, HTTPS verification.
    * *Semantic:* Character-level and word-level TF-IDF vectorization (3-5 n-grams).
3.  **Parallel Detection:**
    * **ML Engine:** XGBoost evaluates structure; Logistic Regression evaluates semantics.
    * **Rule Engine:** Scans for suspicious keywords, direct IP addresses, and missing cryptographic certificates.
4.  **Ensemble Fusion:** A weighted algebraic scoring system synthesizes the probabilities and rule penalties into a final threat verdict.

---

## 📊 Performance Metrics

Evaluated on a strictly balanced, isolated test set (80/20 split) avoiding data leakage:

| Model | Target | Accuracy | ROC-AUC |
| :--- | :--- | :--- | :--- |
| **URL Hybrid Ensemble** | URLs | 0.98 | **0.9936** |
| **Email Hybrid TF-IDF + LR** | Emails | 0.98 | **0.9987** |

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8+
* Google Chrome (for the extension)

### 1. Backend Setup (Django API & Dashboard)
```bash
# Clone the repository
git clone [https://github.com/yourusername/PhishDetect-Pro.git](https://github.com/yourusername/PhishDetect-Pro.git)
cd PhishDetect-Pro/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
python manage.py runserver