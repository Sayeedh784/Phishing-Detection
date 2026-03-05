# PhishDetect Pro (Dataset-Ready)

This is a thesis-grade Hybrid Phishing Detection System.

✅ Supports:
- URL scanning (Rules + XGBoost numeric + TF‑IDF char model)
- Email scanning (Rules + TF‑IDF word model + optional URL-risk integration)

✅ API:
`POST /api/predict/` with JSON: `{ "type": "url" | "email", "text": "..." }`

---

## Dataset Placement (You add manually)

Create these folders (already included in ZIP):

```
backend/data/url/
backend/data/email/
```

### Put your files here:

**URL**
- `backend/data/url/legitimate_urls_500k.csv`
- `backend/data/url/phishing_urls_500k.csv`

**Email**
- `backend/data/email/email_legit.csv`
- `backend/data/email/email_phishing.csv`

These match the uploaded dataset formats:
- URL CSV: columns `url`, `label` (0=legit, 1=phishing)
- Email CSV: columns `email_text`, `label` (0=legit, 1=phishing)

---

## Train Models (Run in backend/)

```bash
cd backend
python ml/train_url.py
python ml/train_email.py
```

Artifacts saved to:
`backend/ml/models/`

---

## Run Server

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Open dashboard:
http://127.0.0.1:8000/

---

## Accuracy Note
This pipeline is designed for high accuracy on large datasets.
Final accuracy depends on dataset quality + balance + cleaning. No leakage is used.
