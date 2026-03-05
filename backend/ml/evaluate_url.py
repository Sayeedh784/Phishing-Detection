import os
import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from .data_loader import load_url_dataset
from .features import extract_url_numeric_features, dicts_to_matrix
from .rules import url_rule_flags, url_rule_score
from joblib import Parallel, delayed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
OUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "reports")
os.makedirs(OUT_DIR, exist_ok=True)

def compute_rule_scores(X_te):
    """Parallelized rule score computation."""
    def process_url(url):
        return url_rule_score(url_rule_flags(url))
    
    return Parallel(n_jobs=-1)(delayed(process_url)(u) for u in X_te)

def main():
    print("[INFO] Loading dataset...")
    df = load_url_dataset(DATA_DIR)

    y = df["label"].astype(int).values
    urls = df["url"].astype(str).values

    print("[INFO] Train-test split...")
    X_tr, X_te, y_tr, y_te = train_test_split(urls, y, test_size=0.2, random_state=42, stratify=y)

    # Load models once for fast access
    print("[INFO] Loading trained models...")
    xgb = joblib.load(os.path.join(MODEL_DIR, "url_xgb.joblib"))
    feat_order = joblib.load(os.path.join(MODEL_DIR, "url_feature_order.joblib"))
    vec = joblib.load(os.path.join(MODEL_DIR, "url_tfidf_vectorizer.joblib"))
    lr = joblib.load(os.path.join(MODEL_DIR, "url_tfidf_lr.joblib"))

    print("[INFO] Extracting numeric features...")
    feat_dicts = [extract_url_numeric_features(u) for u in X_te]
    X_num, _ = dicts_to_matrix(feat_dicts, feature_order=feat_order)

    print("[INFO] Predicting XGBoost probabilities...")
    xgb_p = xgb.predict_proba(X_num)[:, 1]

    print("[INFO] Predicting TF-IDF + LR probabilities...")
    X_tfidf = vec.transform(X_te)
    lr_p = lr.predict_proba(X_tfidf)[:, 1]

    print("[INFO] Computing rule scores...")
    rule_scores = compute_rule_scores(X_te)

    # Hybrid score calculation
    probs = (0.2 * np.array(rule_scores)) + (0.4 * xgb_p) + (0.4 * lr_p)

    y_pred = (probs >= 0.5).astype(int)

    print("\n=== URL HYBRID EVALUATION (FAST) ===")
    print(classification_report(y_te, y_pred))
    auc = roc_auc_score(y_te, probs)
    print("ROC AUC:", auc)

    # Confusion matrix
    cm = confusion_matrix(y_te, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title("URL Hybrid Confusion Matrix")
    plt.savefig(os.path.join(OUT_DIR, "url_confusion_matrix.png"), dpi=300)
    plt.close()

    # ROC curve
    fpr, tpr, _ = roc_curve(y_te, probs)
    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("URL Hybrid ROC Curve")
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(OUT_DIR, "url_roc_curve.png"), dpi=300)
    plt.close()

    print("\n✅ Saved outputs in backend/reports/:")
    print(" - url_confusion_matrix.png")
    print(" - url_roc_curve.png")

if __name__ == "__main__":
    main()
