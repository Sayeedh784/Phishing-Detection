# PhishDetect Pro: A Hybrid Machine Learning and Rule‑Based System for Phishing Detection
(Full thesis text can be generated after you confirm your university format and required chapters.)

## Dataset Columns (Based on your uploaded data)
### URL:
- url (string)
- label (0=legitimate, 1=phishing)

### Email:
- email_text (string)
- label (0=legitimate, 1=phishing)

## Key Cleaning Observations
- `phishing_urls_500k.csv` contains at least one row where the URL value is literally 'url' (bad row).
  The loader automatically removes it.

## Evaluation & Accuracy
Use ROC-AUC + classification report.
Hybrid ensemble improves robustness and explainability.
