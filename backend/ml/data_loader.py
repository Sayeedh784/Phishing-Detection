import os
import pandas as pd
import dask.dataframe as dd  # Using dask for parallel processing

def safe_read_csv(path):
    """Attempt to read a CSV file with default and alternative encoding."""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")

def load_url_dataset(data_dir):
    """Load URL dataset efficiently by parallel processing using Dask."""
    legit_path = os.path.join(data_dir, "url", "legitimate_urls_500k.csv")
    phish_path = os.path.join(data_dir, "url", "phishing_urls_500k.csv")

    paths = [legit_path, phish_path]
    
    # Using Dask to read CSV files in parallel
    frames = []
    for p in paths:
        if os.path.exists(p):
            # Dask can read CSV files in parallel
            ddf = dd.read_csv(p, encoding="latin-1")  # Dask automatically handles large datasets
            # Ensure correct columns and process
            if "url" not in ddf.columns or "label" not in ddf.columns:
                raise ValueError(f"URL CSV must contain 'url' and 'label': {p}")
            ddf = ddf[["url", "label"]]  # Select relevant columns
            frames.append(ddf)

    if not frames:
        raise FileNotFoundError("Missing URL datasets in backend/data/url/")
    
    # Concatenate Dask dataframes into a single dataframe
    df = dd.concat(frames, axis=0).compute()  # Use Dask's compute to bring it to memory (only after processing)
    
    # Handle known issue of 'url' string and clean
    df["url"] = df["url"].astype(str)
    df = df[df["url"].str.lower().ne("url")]

    # Drop missing and duplicate data efficiently
    df = df.dropna(subset=["url", "label"]).drop_duplicates(subset=["url"])

    return df

def load_email_dataset(data_dir):
    """Load Email dataset efficiently by parallel processing using Dask."""
    legit_path = os.path.join(data_dir, "email", "email_legit.csv")
    phish_path = os.path.join(data_dir, "email", "email_phishing.csv")

    paths = [legit_path, phish_path]
    
    # Using Dask to read CSV files in parallel
    frames = []
    for p in paths:
        if os.path.exists(p):
            # Dask can read CSV files in parallel
            ddf = dd.read_csv(p, encoding="latin-1")  # Dask handles large datasets
            # Ensure correct columns and process
            if "email_text" not in ddf.columns or "label" not in ddf.columns:
                raise ValueError(f"Email CSV must contain 'email_text' and 'label': {p}")
            ddf = ddf[["email_text", "label"]]  # Select relevant columns
            frames.append(ddf)

    if not frames:
        raise FileNotFoundError("Missing Email datasets in backend/data/email/")
    
    # Concatenate Dask dataframes into a single dataframe
    df = dd.concat(frames, axis=0).compute()  # Use Dask's compute to bring it to memory (only after processing)

    # Drop missing and duplicate data efficiently
    df = df.dropna(subset=["email_text", "label"]).drop_duplicates(subset=["email_text"])

    return df
