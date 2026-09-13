"""
scraper.py
==========
Extracts, cleans, enriches, and caches the Fortune Global Largest Companies by Revenue
from Wikipedia: https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue
"""

from __future__ import annotations

import io
import re
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

DATA_FILE = Path(__file__).resolve().parent / "largest_companies.csv"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue"

COUNTRY_ISO_MAP = {
    "United States": "USA",
    "China": "CHN",
    "Germany": "DEU",
    "Switzerland": "CHE",
    "United Kingdom": "GBR",
    "Saudi Arabia": "SAU",
    "Japan": "JPN",
    "Singapore": "SGP",
    "France": "FRA",
    "Netherlands": "NLD",
    "South Korea": "KOR",
    "Taiwan": "TWN",
}


def clean_numeric(val: object) -> float | None:
    """Extract float from dirty string containing commas, brackets, signs, etc."""
    if pd.isna(val):
        return None
    val_str = str(val)
    val_str = re.sub(r"\[.*?\]", "", val_str)
    val_str = (
        val_str.replace(",", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace("¥", "")
        .strip()
    )
    if val_str.startswith("(") and val_str.endswith(")"):
        val_str = "-" + val_str[1:-1]
    match = re.search(r"[-+]?\d*\.?\d+", val_str)
    return float(match.group()) if match else None


def clean_text(val: object) -> str:
    """Clean footnote brackets, extra whitespace, and normalize text."""
    if pd.isna(val):
        return ""
    val_str = re.sub(r"\[.*?\]", "", str(val))
    # Normalize internal spaces
    val_str = " ".join(val_str.split()).strip()
    return val_str


def normalize_industry(val: str) -> str:
    """Standardize multi-category strings into clean labels."""
    if not val:
        return "Other"
    val = val.strip()
    if "Retail" in val and "Information technology" in val:
        return "Retail / E-Commerce"
    return val


def scrape_wikipedia_companies() -> pd.DataFrame:
    """Scrape the latest table of largest companies from Wikipedia."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(WIKI_URL, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="wikitable")
    if table is None:
        raise ValueError("Could not find table with class 'wikitable' on Wikipedia page.")

    df = pd.read_html(io.StringIO(str(table)))[0]

    # Flatten multi-level columns if any
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join(col).strip() for col in df.columns.values]

    # Map raw headers
    column_mapping = {}
    for col in df.columns:
        c_lower = col.lower()
        if "rank" in c_lower:
            column_mapping[col] = "Rank"
        elif "name" in c_lower or "company" in c_lower:
            column_mapping[col] = "Company"
        elif "industry" in c_lower:
            column_mapping[col] = "Industry"
        elif "revenue" in c_lower:
            column_mapping[col] = "Revenue (USD)"
        elif "profit" in c_lower:
            column_mapping[col] = "Profit (USD)"
        elif "employee" in c_lower:
            column_mapping[col] = "Employees"
        elif "headquarters" in c_lower or "country" in c_lower:
            column_mapping[col] = "Country"

    df = df.rename(columns=column_mapping)
    required_cols = [
        "Rank",
        "Company",
        "Country",
        "Industry",
        "Revenue (USD)",
        "Profit (USD)",
        "Employees",
    ]
    df = df[[col for col in required_cols if col in df.columns]].copy()

    # Clean text columns
    for col in ["Company", "Country", "Industry"]:
        if col in df.columns:
            df.loc[:, col] = df[col].apply(clean_text)

    # Standardize industry
    if "Industry" in df.columns:
        df.loc[:, "Industry"] = df["Industry"].apply(normalize_industry)

    # Clean numeric columns
    for col in ["Rank", "Revenue (USD)", "Profit (USD)", "Employees"]:
        if col in df.columns:
            df.loc[:, col] = df[col].apply(clean_numeric)

    # Drop rows without Revenue
    df = df.dropna(subset=["Revenue (USD)"]).copy()

    # Cast integer types where appropriate
    df.loc[:, "Rank"] = df["Rank"].astype("Int64")
    df.loc[:, "Employees"] = df["Employees"].astype("Int64")

    # Enrichment: Financial & Productivity Ratios
    # Revenue & Profit are in USD Billions ($B)
    # Revenue (USD) * 1e9 = USD Dollars
    df.loc[:, "Profit Margin (%)"] = (df["Profit (USD)"] / df["Revenue (USD)"]) * 100
    df.loc[:, "Revenue per Employee ($)"] = (df["Revenue (USD)"] * 1e9) / df["Employees"]
    df.loc[:, "Profit per Employee ($)"] = (df["Profit (USD)"] * 1e9) / df["Employees"]
    df.loc[:, "ISO_Alpha3"] = df["Country"].map(COUNTRY_ISO_MAP).fillna("UNK")

    return df


def load_data(force_scrape: bool = False) -> pd.DataFrame:
    """
    Load data from local CSV if present, or scrape if missing/forced.
    Enriches with calculated indicators.
    """
    if not force_scrape and DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        # Ensure enriched columns exist
        if "Profit Margin (%)" not in df.columns:
            df["Profit Margin (%)"] = (df["Profit (USD)"] / df["Revenue (USD)"]) * 100
        if "Revenue per Employee ($)" not in df.columns:
            df["Revenue per Employee ($)"] = (df["Revenue (USD)"] * 1e9) / df["Employees"]
        if "Profit per Employee ($)" not in df.columns:
            df["Profit per Employee ($)"] = (df["Profit (USD)"] * 1e9) / df["Employees"]
        if "ISO_Alpha3" not in df.columns:
            df["ISO_Alpha3"] = df["Country"].map(COUNTRY_ISO_MAP).fillna("UNK")
        return df

    df = scrape_wikipedia_companies()
    df.to_csv(DATA_FILE, index=False)
    return df


if __name__ == "__main__":
    data = load_data(force_scrape=True)
    print(f"Scraped & saved {len(data)} companies to {DATA_FILE}")
    print(data.head())
