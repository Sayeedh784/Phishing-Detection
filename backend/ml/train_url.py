import os
import json
import joblib
import numpy as np
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from joblib import Parallel, delayed
from .data_loader import load_url_dataset
from .features import extract_url_numeric_features, dicts_to_matrix, get_domain
from .rules import url_rule_flags, url_rule_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

FAST_TRAIN = False
FAST_PER_CLASS = 200000

def main():
    try:
        df = load_url_dataset(DATA_DIR)
    except Exception as e:
        print("[WARN]", e)
        return

    # ---- Optional Fast Training ----
    if FAST_TRAIN:
        df0 = df[df.label == 0].sample(FAST_PER_CLASS, random_state=42)
        df1 = df[df.label == 1].sample(FAST_PER_CLASS, random_state=42)
        df = df0._append(df1, ignore_index=True)

    # ---- Auto Trusted Domain List ----
    legit_domains = df[df["label"] == 0]["url"].astype(str).map(get_domain)
    legit_domains = legit_domains[legit_domains.str.len() > 0]
    domain_counts = Counter(legit_domains.tolist())
    TOP_N = 30000
    trusted_domains = [d for d, _ in domain_counts.most_common(TOP_N)]

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, "trusted_domains.json"), "w", encoding="utf-8") as f:
        json.dump(trusted_domains, f, indent=2)
    print(f"[OK] Saved {len(trusted_domains)} trusted domains to ml/models/trusted_domains.json")

    # ---- Labels + URLs ----
    y = df["label"].astype(int).values
    urls = df["url"].astype(str).values

    # ---- Numeric Features ----
    feat_dicts = [extract_url_numeric_features(u) for u in urls]
    X_num, feat_order = dicts_to_matrix(feat_dicts)

    Xnum_tr, Xnum_te, Xtxt_tr, Xtxt_te, y_tr, y_te = train_test_split(
        X_num, urls, y, test_size=0.2, random_state=42, stratify=y
    )

    # ---- XGBoost ----
    xgb = XGBClassifier(
        n_estimators=1200 if FAST_TRAIN else 1500,
        max_depth=6 if FAST_TRAIN else 7,
        learning_rate=0.06 if FAST_TRAIN else 0.04,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        min_child_weight=1,
        gamma=0.1,
        eval_metric="logloss",
        tree_method="hist",
        n_jobs=4,
        random_state=42
    )
    xgb.fit(Xnum_tr, y_tr, eval_set=[(Xnum_te, y_te)], verbose=50)
    xgb_p = xgb.predict_proba(Xnum_te)[:, 1]

    print("\n=== URL Numeric XGBoost ===")
    print(classification_report(y_te, (xgb_p >= 0.5).astype(int)))
    print("ROC AUC:", roc_auc_score(y_te, xgb_p))

    # ---- TF-IDF char + LR ----
    tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=250000 if FAST_TRAIN else 300000
    )
    Xtf_tr = tfidf.fit_transform(Xtxt_tr)
    Xtf_te = tfidf.transform(Xtxt_te)

    lr = LogisticRegression(
        max_iter=400 if FAST_TRAIN else 600,
        class_weight="balanced",
        C=2.0
    )
    lr.fit(Xtf_tr, y_tr)
    lr_p = lr.predict_proba(Xtf_te)[:, 1]

    print("\n=== URL Char TF-IDF + LR ===")
    print(classification_report(y_te, (lr_p >= 0.5).astype(int)))
    print("ROC AUC:", roc_auc_score(y_te, lr_p))

    # ---- Hybrid Ensemble ----
    rule_scores = np.array([url_rule_score(url_rule_flags(u)) for u in Xtxt_te])
    final = (0.2 * rule_scores) + (0.4 * xgb_p) + (0.4 * lr_p)
    pred = (final >= 0.5).astype(int)

    print("\n=== URL Hybrid Ensemble (Rules + XGB + LR) ===")
    print(classification_report(y_te, pred))
    print("ROC AUC:", roc_auc_score(y_te, final))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(xgb, os.path.join(MODEL_DIR, "url_xgb.joblib"))
    joblib.dump(feat_order, os.path.join(MODEL_DIR, "url_feature_order.joblib"))
    joblib.dump(tfidf, os.path.join(MODEL_DIR, "url_tfidf_vectorizer.joblib"))
    joblib.dump(lr, os.path.join(MODEL_DIR, "url_tfidf_lr.joblib"))
    print("\n[OK] URL models saved in backend/ml/models/")

if __name__ == "__main__":
    main()
