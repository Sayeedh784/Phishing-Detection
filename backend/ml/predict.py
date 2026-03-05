import os
import joblib
import numpy as np
from urllib.parse import urlparse
from joblib import Parallel, delayed

from .rules import url_rule_flags, url_rule_score, email_rule_flags, email_rule_score
from .features import extract_url_numeric_features, dicts_to_matrix, preprocess_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

_trusted_cache = None

# Caching the trusted domains for repeated use
def _load_trusted(force_reload=False):
    global _trusted_cache

    if (not force_reload) and (_trusted_cache is not None) and (len(_trusted_cache) > 0):
        return _trusted_cache

    path = os.path.join(MODEL_DIR, "trusted_domains.json")
    if os.path.exists(path):
        try:
            import json
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _trusted_cache = set(data) if isinstance(data, list) else set()
        except Exception:
            _trusted_cache = set()
    else:
        _trusted_cache = set()

    return _trusted_cache

def _normalize_url(url: str) -> str:
    """Strip whitespace and ensure scheme exists."""
    u = str(url).strip()
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u

def _is_trusted_domain(url: str) -> bool:
    try:
        u = _normalize_url(url)
        host = (urlparse(u).netloc or "").lower().split(":")[0]

        trusted = _load_trusted(force_reload=False)

        if not trusted:
            trusted = _load_trusted(force_reload=True)

        return any(host == d or host.endswith("." + d) for d in trusted)
    except Exception:
        return False

def _safe_load(path):
    try:
        return joblib.load(path) if os.path.exists(path) else None
    except Exception:
        return None

def _warnings(url_xgb, url_lr, email_lr):
    w = []
    if url_xgb is None:
        w.append("URL numeric model missing.")
    if url_lr is None:
        w.append("URL text model missing.")
    if email_lr is None:
        w.append("Email model missing.")
    return w

def _top_features(vectorizer, model, text, k=12):
    try:
        vec = vectorizer.transform([text])
        if not hasattr(model, "coef_"):
            return []
        coef = model.coef_[0]
        nz = vec.nonzero()[1]
        feats = vectorizer.get_feature_names_out()
        scored = [(feats[i], float(coef[i])) for i in nz]
        scored = sorted(scored, key=lambda x: abs(x[1]), reverse=True)[:k]
        return [s[0] for s in scored]
    except Exception:
        return []

# Parallelized URL Prediction
def _predict_url_for_list(urls):
    """Parallelize URL prediction for a list of URLs."""
    return Parallel(n_jobs=-1)(delayed(predict_url)(url) for url in urls)

# ================================
# URL Prediction (Hybrid)
# ================================
def predict_url(url: str):
    url_clean = _normalize_url(url)

    flags = url_rule_flags(url_clean)
    rule_s = url_rule_score(flags)

    xgb = _safe_load(os.path.join(MODEL_DIR, "url_xgb.joblib"))
    feat_order = _safe_load(os.path.join(MODEL_DIR, "url_feature_order.joblib"))
    lr = _safe_load(os.path.join(MODEL_DIR, "url_tfidf_lr.joblib"))
    vec = _safe_load(os.path.join(MODEL_DIR, "url_tfidf_vectorizer.joblib"))

    xgb_s = 0.0
    lr_s = 0.0
    top = []

    # Numeric model
    if xgb is not None and feat_order is not None:
        X, _ = dicts_to_matrix([extract_url_numeric_features(url_clean)], feature_order=feat_order)
        try:
            xgb_s = float(xgb.predict_proba(X)[0, 1])
        except Exception:
            xgb_s = 0.0

    # Text model
    if lr is not None and vec is not None:
        try:
            lr_s = float(lr.predict_proba(vec.transform([url_clean]))[0, 1])
            top = _top_features(vec, lr, url_clean)
        except Exception:
            lr_s = 0.0

    final = (0.2 * rule_s) + (0.4 * xgb_s) + (0.4 * lr_s)

    # Trusted Domain Hard Override
    if _is_trusted_domain(url_clean) and url_clean.lower().startswith("https://"):
        return {
            "label": "legitimate",
            "score": 0.05,
            "explanation": {
                "trusted_domain": True,
                "rule_based_flags": [],
                "top_features": top,
                "model_breakdown": {
                    "rule": round(rule_s, 4),
                    "xgboost": round(xgb_s, 4),
                    "lr": round(lr_s, 4),
                },
                "note": "Trusted domain override applied to prevent false positives.",
            },
        }

    label = "phishing" if final >= 0.5 else "legitimate"

    return {
        "label": label,
        "score": round(float(final), 6),
        "explanation": {
            "trusted_domain": _is_trusted_domain(url_clean),
            "rule_based_flags": flags,
            "top_features": top,
            "model_breakdown": {
                "rule": round(rule_s, 4),
                "xgboost": round(xgb_s, 4),
                "lr": round(lr_s, 4),
            },
            "warnings": _warnings(xgb, lr, None),
        },
    }

# ================================
# EMAIL Prediction (Hybrid)
# ================================
def predict_email(text: str):
    cleaned = preprocess_email(text)
    flags, urls = email_rule_flags(text)
    rule_s = email_rule_score(flags)

    email_lr = _safe_load(os.path.join(MODEL_DIR, "email_lr.joblib"))
    email_vec = _safe_load(os.path.join(MODEL_DIR, "email_vectorizer.joblib"))

    ml_s = 0.0
    top = []

    if email_lr is not None and email_vec is not None:
        try:
            ml_s = float(email_lr.predict_proba(email_vec.transform([cleaned]))[0, 1])
            top = _top_features(email_vec, email_lr, cleaned)
        except Exception:
            ml_s = 0.0

    # URL risk integration (if URLs exist)
    url_risks = _predict_url_for_list(urls[:5])
    url_risk = max([url["score"] for url in url_risks], default=0.0)

    # New hybrid formula
    final = (0.25 * rule_s) + (0.55 * ml_s) + (0.20 * url_risk)

    # Strong phishing override rules
    if "credential_request" in flags and len(urls) > 0:
        label = "phishing"
        final = max(final, 0.92)
    elif url_risk >= 0.80 and len(urls) > 0:
        label = "phishing"
        final = max(final, 0.88)
    elif "urgent_language" in flags and ("credential_request" in flags or len(urls) > 0):
        label = "phishing"
        final = max(final, 0.85)
    else:
        label = "phishing" if final >= 0.30 else "legitimate"

    return {
        "label": label,
        "score": round(float(final), 6),
        "explanation": {
            "rule_based_flags": flags,
            "top_features": top,
            "url_risk_summary": {
                "found_urls": len(urls),
                "max_url_risk": round(url_risk, 6),
            },
            "model_breakdown": {
                "rule": round(rule_s, 4),
                "ml": round(ml_s, 4),
                "url_risk": round(url_risk, 4),
            },
            "warnings": _warnings(None, None, email_lr),
            "note": "Email scoring adjusted for higher phishing recall (lower false negatives)."
        },
    }
