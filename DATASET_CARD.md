# 🌐 Fortune Global 50 — Largest Companies Intelligence & Benchmarks

<div align="center">

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg?style=for-the-badge)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Kaggle Usability](https://img.shields.io/badge/Kaggle-Usability_10.0-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com)
[![Records](https://img.shields.io/badge/Records-50_Enterprises-2563EB?style=for-the-badge)](#-summary-statistics--benchmark-baselines)
[![Features](https://img.shields.io/badge/Features-11_Metrics-10B981?style=for-the-badge)](#-data-dictionary)
[![Format](https://img.shields.io/badge/Format-CSV_&_Excel-F59E0B?style=for-the-badge)](#)

**An authoritative, validated corporate dataset tracking the 50 largest companies in the world by gross revenue, net profitability, global workforce, and capital efficiency metrics.**

</div>

---

## 📌 Context & Overview

Understanding the architecture of global corporate power is fundamental to economics, strategic finance, and data science. While gross revenue represents sheer market turnover, true business dominance is determined by net profit conversion, intellectual property pricing power, and workforce leverage.

This dataset compiles verified financial figures and employee counts from the **Fortune Global 500 monitoring sources** and Wikipedia's corporate intelligence index. It includes standard corporate attributes enriched with calculated financial health ratios and ISO geographic codes for global spatial modeling.

---

## 🎯 Strategic Analytical Questions Answered

1. **The Scale Paradox**: Do the world's largest revenue generators (e.g. Walmart, Amazon) also produce the largest profits, or does profit concentrate in high-margin technology monopolies?
2. **Sector Margin Sovereignty**: How do net profit margins compare across high-barrier industries (Semiconductors, Oil & Gas, Tech) versus high-volume low-margin processors (Retail, Healthcare)?
3. **Geopolitical Duopoly**: How concentrated is corporate wealth between the United States and China versus the European Union and Asia-Pacific?
4. **Workforce Capital Efficiency**: Which enterprises generate the highest revenue and net profit per employee (e.g., commodity traders and fabless chip designers vs. massive retail labor forces)?
5. **Pareto Concentration**: Does the 80/20 rule apply to macro corporate revenue, and how many firms control 50% of the total revenue pool?

---

## 🗂️ Data Dictionary & Feature Schema

| Column Name | Data Type | Nulls | Example Value | Definition & Notes |
|:---|:---:|:---:|:---|:---|
| `Rank` | `int64` | `0` | `1` | Global revenue ranking from 1 to 50. |
| `Company` | `string` | `0` | `Amazon` | Registered enterprise legal name. |
| `Country` | `string` | `0` | `United States` | Sovereign nation of corporate headquarters. |
| `Industry` | `string` | `0` | `Retail / E-Commerce` | Primary industry sector classification. |
| `Revenue (USD)` | `float64` | `0` | `716.0` | Total gross annual revenue in **USD Billions ($B)**. |
| `Profit (USD)` | `float64` | `1` | `79.9` | Total net annual profit in **USD Billions ($B)**. *(NaN for private entities such as Schwarz Gruppe)* |
| `Employees` | `int64` | `0` | `1,576,000` | Full-time global employee headcount. |
| `Profit Margin (%)` | `float64` | `1` | `11.16` | Net margin ratio: `(Profit (USD) / Revenue (USD)) * 100`. |
| `Revenue per Employee ($)` | `float64` | `0` | `454,315` | Revenue efficiency: `(Revenue in USD) / Employees`. |
| `Profit per Employee ($)` | `float64` | `1` | `50,698` | Profit leverage: `(Profit in USD) / Employees`. |
| `ISO_Alpha3` | `string` | `0` | `USA` | Standard ISO 3166-1 alpha-3 nation code for choropleth mapping. |

---

## 📊 Summary Statistics & Cohort Baselines

| Key Benchmark Indicator | Cohort Aggregate Value | Notes & Leader |
|:---|:---:|:---|
| **Total Tracked Enterprises** | `50 Companies` | Verified Fortune Global 50 cohort |
| **Combined Revenue Pool** | `$13.94 Trillion USD` | ~14% of Global Nominal GDP |
| **Combined Net Profit** | `$1.46 Trillion USD` | Aggregate net profit conversion: **10.48%** |
| **Total Global Workforce** | `16,767,434 Workers` | Global enterprise labor footprint |
| **Top Revenue Leader** | `Amazon ($716.0B)` | Followed closely by Walmart ($713.0B) |
| **Top Net Profit Leader** | `Alphabet ($132.0B)` | Followed by Saudi Aramco & Apple |
| **Largest Global Employer** | `Walmart (2,100,000)` | Followed by Amazon (1,576,000) |
| **Highest Profit Margin** | `Nvidia (55.81%)` | High-margin AI semiconductor dominance |
| **Highest Revenue / Worker** | `Vitol ($212.18M)` | Commodity energy asset trading leverage |

---

## 🚀 Starter Code (Python / Pandas)

```python
import pandas as pd

# Load dataset
df = pd.read_csv("largest_companies.csv")

# Quick diagnostics
print(f"Loaded {len(df)} companies across {df['Country'].nunique()} sovereign nations.")
print(f"Total Revenue Pool: ${df['Revenue (USD)'].sum():,.1f} Billion USD")
print(f"Total Net Profit:   ${df['Profit (USD)'].dropna().sum():,.1f} Billion USD")

# Top 5 Profit Margin Leaders (excluding nulls)
margin_leaders = df.dropna(subset=["Profit Margin (%)"]).nlargest(5, "Profit Margin (%)")
print("\nTop 5 Margin Leaders:")
print(margin_leaders[["Company", "Industry", "Profit Margin (%)", "Revenue (USD)", "Profit (USD)"]])
```

---

## 💡 Key Exploratory Findings

1. **Geopolitical Concentration:** The United States (24 companies, $7.05T revenue) and China (11 companies, $3.05T revenue) form a duopoly capturing **72.5%** of global enterprise revenue.
2. **Margin Kings vs. Volume Titans:** High-volume distributors (Walmart, Amazon, Trafigura) operate on thin margins (1%–11%), while intellectual property monopolies (Nvidia, Alphabet, Microsoft) yield net profit margins exceeding **25%–55%**.
3. **Extreme Workforce Leverage:** Energy trading entities and chip designers generate tens of millions in revenue per employee, outperforming labor-intensive retail logistics by several orders of magnitude.

---

## 📜 Provenance & License

- **Source:** Wikipedia & Fortune Global 500 monitoring indices.
- **Collection Method:** Beautiful Soup 4 automated web-scraper with automated regex cleaning and cross-table validation.
- **License:** **Creative Commons Zero 1.0 (CC0 1.0)** — Dedicated to the Public Domain. Free for educational, academic, commercial, and research use without restriction.
