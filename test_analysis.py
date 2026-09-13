"""
test_analysis.py
================
Comprehensive automated test suite for the Fortune Global 50 Intelligence suite.
Verifies data extraction, financial metrics, KPI calculators, and chart generators.
"""

from pathlib import Path
import pandas as pd
import analysis
from scraper import load_data, clean_numeric, clean_text, normalize_industry


def test_clean_numeric():
    assert clean_numeric("$716.0") == 716.0
    assert clean_numeric("1,576,000") == 1576000.0
    assert clean_numeric("(12.5)") == -12.5
    assert clean_numeric("N/A") is None
    assert clean_numeric(None) is None


def test_clean_text():
    assert clean_text("Amazon[5]") == "Amazon"
    assert clean_text("  United   States  ") == "United States"


def test_normalize_industry():
    assert normalize_industry("Retail  Information technology") == "Retail / E-Commerce"
    assert normalize_industry("Oil and gas") == "Oil and gas"


def test_dataset_loading_and_columns():
    df = load_data(force_scrape=False)
    assert not df.empty
    assert len(df) == 50

    required_cols = [
        "Rank",
        "Company",
        "Country",
        "Industry",
        "Revenue (USD)",
        "Profit (USD)",
        "Employees",
        "Profit Margin (%)",
        "Revenue per Employee ($)",
        "Profit per Employee ($)",
        "ISO_Alpha3",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column {col}"

    assert df["Rank"].min() == 1
    assert df["Rank"].max() == 50
    assert df["Revenue (USD)"].notna().all()


def test_kpi_calculations():
    df = load_data(force_scrape=False)
    kpis = analysis.get_kpis(df, df)

    assert kpis["total_companies"] == 50
    assert kpis["total_share_pct"] == 100.0
    assert kpis["highest_revenue_company"] == "Amazon"
    assert kpis["highest_revenue_val"] == 716.0
    assert kpis["highest_revenue_rank"] == 1
    assert kpis["highest_profit_company"] == "Alphabet"
    assert kpis["highest_profit_val"] == 132.0
    assert kpis["largest_employer_company"] == "Walmart"
    assert kpis["largest_employer_count"] == 2100000
    assert kpis["total_revenue_b"] > 13000
    assert kpis["total_employees"] > 16000000


def test_filter_dataframe():
    df = load_data(force_scrape=False)

    # Filter by Country
    us_only = analysis.filter_dataframe(df, countries=["United States"])
    assert len(us_only) == 24
    assert (us_only["Country"] == "United States").all()

    # Filter by search
    apple_search = analysis.filter_dataframe(df, search_query="apple")
    assert len(apple_search) == 1
    assert apple_search.iloc[0]["Company"] == "Apple"

    # Filter by Revenue range
    high_rev = analysis.filter_dataframe(df, min_revenue=400.0)
    assert len(high_rev) >= 5


def test_charts_generation():
    df = load_data(force_scrape=False)

    f1 = analysis.chart_top10_revenue(df)
    assert f1 is not None

    f2 = analysis.chart_top10_profit(df)
    assert f2 is not None

    f3 = analysis.chart_companies_by_industry(df)
    assert f3 is not None

    f4 = analysis.chart_companies_by_country(df)
    assert f4 is not None

    f5 = analysis.chart_revenue_by_country_map(df)
    assert f5 is not None

    f6 = analysis.chart_revenue_by_country_bar(df)
    assert f6 is not None

    f7 = analysis.chart_revenue_by_industry_bar(df)
    assert f7 is not None

    f8 = analysis.chart_revenue_vs_profit(df)
    assert f8 is not None

    f9 = analysis.chart_margin_by_industry(df)
    assert f9 is not None

    f10 = analysis.chart_revenue_per_employee(df)
    assert f10 is not None

    f11, r1, r2 = analysis.chart_headcount_correlation(df)
    assert f11 is not None and isinstance(r1, float) and isinstance(r2, float)

    f12 = analysis.chart_distribution_diagnostics(df)
    assert f12 is not None


def test_company_profile():
    df = load_data(force_scrape=False)
    prof = analysis.get_company_profile(df, "Amazon")
    assert prof["Company"] == "Amazon"
    assert prof["Rank"] == 1
    assert prof["Revenue"] == 716.0
    assert prof["Ranks"]["Revenue"] == 1
    assert "Global_Median" in prof


def test_compare_companies():
    df = load_data(force_scrape=False)
    fig, comp_df = analysis.compare_companies(df, "Amazon", "Walmart")
    assert fig is not None
    assert not comp_df.empty
    assert "Amazon" in comp_df.columns
    assert "Walmart" in comp_df.columns


def test_phase4_profit_margin_and_quadrant():
    df = load_data(force_scrape=False)

    # Top Profit Margins
    f_margin = analysis.chart_top_profit_margins(df)
    assert f_margin is not None

    # Capital Efficiency Quadrant
    f_quad = analysis.chart_capital_efficiency_quadrant(df)
    assert f_quad is not None


def test_phase4_benchmarks_and_pareto():
    df = load_data(force_scrape=False)

    # Industry Benchmarks
    ind_bench = analysis.get_industry_benchmarks(df)
    assert not ind_bench.empty
    assert "Industry" in ind_bench.columns
    assert "Total_Revenue" in ind_bench.columns
    f_ind = analysis.chart_industry_benchmarks(ind_bench)
    assert f_ind is not None

    # Country Benchmarks
    cntry_bench = analysis.get_country_benchmarks(df)
    assert not cntry_bench.empty
    assert "Country" in cntry_bench.columns
    f_cntry = analysis.chart_country_benchmarks(cntry_bench)
    assert f_cntry is not None

    # Pareto Concentration
    p_stats = analysis.get_revenue_concentration_stats(df)
    assert p_stats["total_revenue"] > 13000
    assert p_stats["top5_share"] > 0
    assert p_stats["top10_share"] > p_stats["top5_share"]
    assert p_stats["half_count"] <= 25

    f_pareto = analysis.chart_pareto_revenue_concentration(df)
    assert f_pareto is not None


def test_phase4_business_questions():
    df = load_data(force_scrape=False)
    questions = analysis.get_business_questions_answers(df)
    assert len(questions) == 6
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "entity" in q
        assert "metric" in q
        assert "answer" in q
        assert q["entity"] != "N/A"
        assert len(q["answer"]) > 10


def test_phase4_company_profile_benchmark():
    df = load_data(force_scrape=False)
    f_bench = analysis.chart_company_profile_benchmark(df, "Apple")
    assert f_bench is not None

    # Private company with NaN profit (Schwarz Gruppe)
    f_private = analysis.chart_company_profile_benchmark(df, "Schwarz Gruppe")
    assert f_private is not None


def test_phase4_empty_edge_cases():
    empty_df = pd.DataFrame(
        columns=[
            "Rank", "Company", "Country", "Industry",
            "Revenue (USD)", "Profit (USD)", "Employees",
            "Profit Margin (%)", "Revenue per Employee ($)", "ISO_Alpha3"
        ]
    )

    # Empty KPIs
    kpis = analysis.get_kpis(empty_df, empty_df)
    assert kpis["total_companies"] == 0

    # Empty Charts
    assert analysis.chart_top10_revenue(empty_df) is not None
    assert analysis.chart_top10_profit(empty_df) is not None
    assert analysis.chart_top_profit_margins(empty_df) is not None
    assert analysis.chart_capital_efficiency_quadrant(empty_df) is not None
    assert analysis.chart_pareto_revenue_concentration(empty_df) is not None

    # Empty Questions
    questions = analysis.get_business_questions_answers(empty_df)
    assert len(questions) == 6
    assert questions[0]["entity"] == "N/A"

    # Empty Concentration Stats
    stats = analysis.get_revenue_concentration_stats(empty_df)
    assert stats["total_revenue"] == 0.0


def test_phase7_excel_export():
    df = load_data(force_scrape=False)

    # 1. Full Dataset Export
    buf_full = analysis.generate_excel_export(df, "All Companies")
    assert buf_full is not None
    assert len(buf_full.getvalue()) > 5000

    # 2. Filtered Dataset Export
    df_us = df[df["Country"] == "United States"]
    buf_filt = analysis.generate_excel_export(df_us, "Country: United States")
    assert buf_filt is not None
    assert len(buf_filt.getvalue()) > 3000

    # 3. Empty Dataset Export
    buf_empty = analysis.generate_excel_export(df.iloc[0:0], "Zero Companies")
    assert buf_empty is not None
    assert len(buf_empty.getvalue()) > 1000

    # 4. Filename Generator
    fn1 = analysis.get_export_filename()
    assert fn1.startswith("global50_all_companies_") and fn1.endswith(".xlsx")

    fn2 = analysis.get_export_filename(countries=["United States"], industries=["Oil and gas"])
    assert "United_States" in fn2 and "Oil_and_gas" in fn2

    fn_csv = analysis.get_export_filename(ext="csv")
    assert fn_csv.endswith(".csv")


if __name__ == "__main__":
    test_clean_numeric()
    test_clean_text()
    test_normalize_industry()
    test_dataset_loading_and_columns()
    test_kpi_calculations()
    test_filter_dataframe()
    test_charts_generation()
    test_company_profile()
    test_compare_companies()
    test_phase4_profit_margin_and_quadrant()
    test_phase4_benchmarks_and_pareto()
    test_phase4_business_questions()
    test_phase4_company_profile_benchmark()
    test_phase4_empty_edge_cases()
    test_phase7_excel_export()
    print("ALL TESTS PASSED SUCCESSFULLY! (100% PASS)")


