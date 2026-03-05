import os
import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from .data_loader import load_email_dataset
from .features import preprocess_email
from .rules import email_rule_flags, email_rule_score
from .predict import predict_url
from joblib import Parallel, delayed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
OUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "reports")
os.makedirs(OUT_DIR, exist_ok=True)

def compute_rule_and_url_scores(X_te):
    """Parallelized rule and URL risk score computation."""
    def process_email(raw_text):
        flags, urls = email_rule_flags(raw_text)
        rule_score = email_rule_score(flags)
        url_risk_score = 0.0
        if urls:
            try:
                url_risk_score = max(predict_url(u)["score"] for u in urls[:3])
            except Exception:
                pass
        return rule_score, url_risk_score
    
    return Parallel(n_jobs=-1)(delayed(process_email)(raw_text) for raw_text in X_te)

def main():
    print("[INFO] Loading email dataset...")
    df = load_email_dataset(DATA_DIR)

    y = df["label"].astype(int).values
    emails = df["email_text"].astype(str).values

    print("[INFO] Preprocessing emails...")
    emails_clean = np.array([preprocess_email(x) for x in emails])

    print("[INFO] Train-test split...")
    X_tr, X_te, y_tr, y_te = train_test_split(emails_clean, y, test_size=0.2, random_state=42, stratify=y)

    print("[INFO] Loading trained email model + vectorizer...")
    email_vec = joblib.load(os.path.join(MODEL_DIR, "email_vectorizer.joblib"))
    email_lr = joblib.load(os.path.join(MODEL_DIR, "email_lr.joblib"))

    print("[INFO] Vectorizing test emails...")
    X_vec = email_vec.transform(X_te)

    print("[INFO] Predicting ML probabilities...")
    ml_probs = email_lr.predict_proba(X_vec)[:, 1]

    print("[INFO] Computing rule + URL risk scores...")
    rule_scores, url_risk_scores = compute_rule_and_url_scores(X_te)

    # Updated Hybrid formula
    probs = (0.25 * np.array(rule_scores)) + (0.55 * ml_probs) + (0.20 * np.array(url_risk_scores))

    # Updated threshold
    y_pred = (probs >= 0.30).astype(int)

    print("\n=== EMAIL HYBRID EVALUATION (UPDATED) ===")
    print(classification_report(y_te, y_pred))

    auc = roc_auc_score(y_te, probs)
    print("ROC AUC:", auc)

    # Confusion matrix
    cm = confusion_matrix(y_te, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title("Email Hybrid Confusion Matrix (Updated Threshold)")
    plt.savefig(os.path.join(OUT_DIR, "email_confusion_matrix_updated.png"), dpi=300)
    plt.close()

    # ROC curve
    fpr, tpr, _ = roc_curve(y_te, probs)
    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Email Hybrid ROC Curve (Updated Threshold)")
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(OUT_DIR, "email_roc_curve_updated.png"), dpi=300)
    plt.close()

    print("\n✅ Saved updated outputs in backend/reports/:")
    print(" - email_confusion_matrix_updated.png")
    print(" - email_roc_curve_updated.png")

if __name__ == "__main__":
    main()
