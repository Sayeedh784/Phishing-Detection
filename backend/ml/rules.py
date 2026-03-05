import math, re, os, json
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
  "login","verify","update","secure","account","bank","confirm","password","free",
  "bonus","click","signin","security","invoice","webscr","paypal"
]
URGENT_WORDS = ["urgent","immediately","act now","verify now","suspend","limited time","final warning"]
CRED_WORDS = ["password","otp","pin","credit card","bank","account number","login credentials"]

def _entropy(s:str)->float:
    if not s: return 0.0
    freq={}
    for ch in s: freq[ch]=freq.get(ch,0)+1
    ent=0.0
    for c in freq.values():
        p=c/len(s)
        ent -= p*math.log2(p)
    return ent

def url_rule_flags(url:str):
    flags=[]
    u=url.strip()
    p=urlparse(u)
    host=(p.netloc or "").lower()
    # whitelist: avoid keyword-only false positives for trusted domains
    if host in TRUSTED_DOMAINS and (not re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", host)):
        flags=[]
        if not u.lower().startswith("https://"): flags.append("no_https")
        if "@" in u: flags.append("contains_at_symbol")
        if len(u) > 75: flags.append("excessive_length")
        if host.count(".") >= 4: flags.append("too_many_subdomains")
        if _entropy(u) >= 4.2: flags.append("high_entropy")
        return flags
    if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", host): flags.append("contains_ip")
    if not u.lower().startswith("https://"): flags.append("no_https")
    if "@" in u: flags.append("contains_at_symbol")
    if len(u) > 75: flags.append("excessive_length")
    if host.count(".") >= 4: flags.append("too_many_subdomains")
    if any(k in u.lower() for k in SUSPICIOUS_KEYWORDS): flags.append("suspicious_keywords")
    if _entropy(u) >= 4.2: flags.append("high_entropy")
    return flags

def url_rule_score(flags):
    weights={"contains_ip":0.25,"no_https":0.15,"contains_at_symbol":0.10,"excessive_length":0.10,
             "too_many_subdomains":0.10,"suspicious_keywords":0.20,"high_entropy":0.10}
    return min(1.0, sum(weights.get(f,0) for f in flags))

def email_rule_flags(text:str):
    t=text.lower()
    flags=[]
    if any(w in t for w in URGENT_WORDS): flags.append("urgent_language")
    if any(w in t for w in CRED_WORDS): flags.append("credential_request")
    if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", t): flags.append("contains_ip_link")
    urls=re.findall(r"https?://\S+", t)
    if len(urls) >= 3: flags.append("multiple_external_urls")
    if t.count("!") >= 3: flags.append("excessive_exclamation")
    return flags, urls

def email_rule_score(flags):
    weights={"urgent_language":0.25,"credential_request":0.35,"contains_ip_link":0.15,"multiple_external_urls":0.15,"excessive_exclamation":0.10}
    return min(1.0, sum(weights.get(f,0) for f in flags))

import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

def load_trusted_domains():
    path = os.path.join(MODEL_DIR, "trusted_domains.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
        except Exception:
            return set()
    return set()

# ✅ GLOBAL VARIABLE (must exist before url_rule_flags runs)
TRUSTED_DOMAINS = load_trusted_domains()
