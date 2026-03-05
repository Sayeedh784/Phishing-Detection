# Thesis Fixes Included (False Positive/Negative Control)

## 1) URL Trusted Domain Whitelist
- Prevents false positives such as `https://github.com/login`
- Implemented in:
  - `backend/ml/rules.py` (ignores keyword-only flags for trusted domains)
  - `backend/ml/predict.py` (soft-guard for trusted HTTPS domains)

## 2) Email High-Confidence Overrides
- Any `credential_request` + URL => phishing (prevents false negatives)
- High URL risk + URL => phishing

## 3) Important
- Always train models:
  - `python -m ml.train_url`
  - `python -m ml.train_email`
- Delete old models using `CLEAR_CACHE_AND_MODELS.bat` before retraining.

## 4) Automatic Trusted Domains
- Generated from legitimate URL dataset during `python -m ml.train_url`
- Saved to `backend/ml/models/trusted_domains.json`
