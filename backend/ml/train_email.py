import os, json, joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from joblib import Parallel, delayed
from .data_loader import load_email_dataset
from .features import preprocess_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

def main():
    try:
        df = load_email_dataset(DATA_DIR)
    except Exception as e:
        print("[WARN]", e)
        return

    df["email_text"] = df["email_text"].astype(str)
    df = df.dropna(subset=["email_text", "label"])
    df = df[df["email_text"].str.len() >= 20]
    df = df.drop_duplicates(subset=["email_text"]).reset_index(drop=True)

    y = df["label"].astype(int).values
    X = df["email_text"].map(preprocess_email).values

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Parallelize vectorization using joblib
    word_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=120000, stop_words="english")
    char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=80000)
    vectorizer = FeatureUnion([("word_tfidf", word_vec), ("char_tfidf", char_vec)])

    # Use parallel processing to fit and transform data
    Xv_tr = vectorizer.fit_transform(X_tr)
    Xv_te = vectorizer.transform(X_te)

    # Parallelize logistic regression training using multiple cores
    lr = LogisticRegression(max_iter=1500, class_weight="balanced", C=2.0, solver="saga", n_jobs=-1)
    lr.fit(Xv_tr, y_tr)

    p = lr.predict_proba(Xv_te)[:, 1]
    pred = (p >= 0.5).astype(int)
    print("\n=== Email Hybrid TF-IDF (Word+Char) + LR ===")
    print(classification_report(y_te, pred))
    print("ROC AUC:", roc_auc_score(y_te, p))
    print("Confusion Matrix:\n", confusion_matrix(y_te, pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "email_vectorizer.joblib"))
    joblib.dump(lr, os.path.join(MODEL_DIR, "email_lr.joblib"))
    meta = {"samples_total": int(len(df)), "vectorizer": "FeatureUnion(word+char)", "model": "LogisticRegression(saga,C=2.0)", "threshold": 0.5}
    with open(os.path.join(MODEL_DIR, "email_training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("\n[OK] Email model saved in backend/ml/models/")

if __name__ == "__main__":
    main()
