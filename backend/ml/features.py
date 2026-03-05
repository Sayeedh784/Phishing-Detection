import re
import numpy as np
from urllib.parse import urlparse
import tldextract

def extract_url_numeric_features(url: str):
    u=url.strip()
    p=urlparse(u)
    host=p.netloc or ""
    path=p.path or ""
    query=p.query or ""
    ext=tldextract.extract(u)
    domain=".".join([x for x in [ext.domain, ext.suffix] if x])
    return {
      "url_length":len(u),
      "hostname_length":len(host),
      "path_length":len(path),
      "query_length":len(query),
      "num_digits":sum(ch.isdigit() for ch in u),
      "num_special":sum(not ch.isalnum() for ch in u),
      "count_dots":u.count("."),
      "count_hyphen":u.count("-"),
      "count_at":u.count("@"),
      "count_question":u.count("?"),
      "count_equal":u.count("="),
      "count_slash":u.count("/"),
      "count_www":1 if "www" in host.lower() else 0,
      "count_https":1 if u.lower().startswith("https") else 0,
      "tld_length":len(ext.suffix or ""),
      "domain_length":len(domain),
      "subdomain_length":len(ext.subdomain or ""),
    }

def dicts_to_matrix(dict_list, feature_order=None):
    keys = feature_order or sorted(dict_list[0].keys())
    X=np.array([[d.get(k,0) for k in keys] for d in dict_list], dtype=float)
    return X, keys

def preprocess_email(text:str):
    t=text.lower()
    t=re.sub(r"<[^>]+>", " ", t)
    t=re.sub(r"https?://\S+", " URLTOKEN ", t)
    t=re.sub(r"[^a-z0-9\s]", " ", t)
    t=re.sub(r"\s+"," ",t).strip()
    return t


from urllib.parse import urlparse

def get_domain(url: str) -> str:
    
    try:
        u = str(url).strip()
        if not u:
            return ""

        # ✅ Add scheme if missing so urlparse works
        if not u.startswith(("http://", "https://")):
            u = "http://" + u

        host = (urlparse(u).netloc or "").lower()
        host = host.split(":")[0]
        host = host.lstrip("www.")   # ✅ remove leading www.
        return host
    except Exception:
        return ""


