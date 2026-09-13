"""
test_e2e_qa.py
==============
Phase 5 Comprehensive QA and Production Readiness verification suite.
Validates data correctness, edge cases, filter permutations, and view render functions.
"""

import sys
import numpy as np
import pandas as pd
import analysis
import openpyxl
from scraper import load_data


def run_qa_suite():
    print("--- 1. LOADING DATASET ---")
    df = load_data(force_scrape=False)
    assert len(df) == 50, f"Expected 50 records, got {len(df)}"
    print("[PASS] 50 records loaded successfully.")

    print("\n--- 2. VERIFYING DATA CORRECTNESS & NO HARDCODING ---")
    kpis = analysis.get_kpis(df, df)

    # Actual dataframe checks
    assert kpis["total_companies"] == len(df), "Total companies mismatch"
    
    top_rev_row = df.sort_values(by="Revenue (USD)", ascending=False).iloc[0]
    assert kpis["highest_revenue_company"] == top_rev_row["Company"]
    assert kpis["highest_revenue_val"] == top_rev_row["Revenue (USD)"]
    assert kpis["highest_revenue_rank"] == int(top_rev_row["Rank"])
    print(f"[PASS] Highest Revenue dynamically verified: {kpis['highest_revenue_company']} (${kpis['highest_revenue_val']:.0f}B, Rank #{kpis['highest_revenue_rank']})")

    clean_prof = df.dropna(subset=["Profit (USD)"])
    top_prof_row = clean_prof.sort_values(by="Profit (USD)", ascending=False).iloc[0]
    assert kpis["highest_profit_company"] == top_prof_row["Company"]
    assert kpis["highest_profit_val"] == top_prof_row["Profit (USD)"]
    print(f"[PASS] Highest Profit dynamically verified: {kpis['highest_profit_company']} (${kpis['highest_profit_val']:.0f}B, Rank #{kpis['highest_profit_rank']})")

    top_emp_row = df.sort_values(by="Employees", ascending=False).iloc[0]
    assert kpis["largest_employer_company"] == top_emp_row["Company"]
    assert kpis["largest_employer_count"] == top_emp_row["Employees"]
    print(f"[PASS] Largest Employer dynamically verified: {kpis['largest_employer_company']} ({kpis['largest_employer_count']:,} workers, Rank #{kpis['largest_employer_rank']})")

    # Formatting checks
    assert analysis.format_kpi_number(716.0, is_currency=True, is_billions_input=True) == "$716B"
    assert analysis.format_kpi_number(132.0, is_currency=True, is_billions_input=True) == "$132B"
    assert analysis.format_kpi_number(2100000) == "2.1M"
    print("[PASS] Number formatting verified: $716B, $132B, 2.1M")

    print("\n--- 3. TESTING FILTER PERMUTATIONS ---")
    # No filters
    f0 = analysis.filter_dataframe(df)
    assert len(f0) == 50
    print("[PASS] Filter [None]: 50 results")

    # Single filter: Country
    f_us = analysis.filter_dataframe(df, countries=["United States"])
    assert len(f_us) == 24
    print("[PASS] Filter [Country = US]: 24 results")

    # Single filter: Industry
    f_oil = analysis.filter_dataframe(df, industries=["Oil and gas"])
    assert len(f_oil) == 8
    print("[PASS] Filter [Industry = 'Oil and gas']: 8 results")

    # Multiple filters: Country + Industry
    f_multi = analysis.filter_dataframe(df, countries=["United States"], industries=["Oil and gas"])
    assert len(f_multi) >= 2
    print(f"[PASS] Filter [Country = US AND Industry = Oil and gas]: {len(f_multi)} results")

    # Narrow filter: Single company
    f_single = analysis.filter_dataframe(df, search_query="apple")
    assert len(f_single) == 1
    print("[PASS] Filter [Search = 'apple']: 1 result (Apple)")

    # Zero-result filter
    f_zero = analysis.filter_dataframe(df, search_query="xyznonexistentcompany")
    assert len(f_zero) == 0
    print("[PASS] Filter [Search = nonexistent]: 0 results (Empty state)")

    print("\n--- 4. TESTING ALL CHART GENERATORS & RESILIENCE ---")
    test_datasets = [
        ("Full Universe (50)", df),
        ("US Only (24)", f_us),
        ("Oil and gas Only (8)", f_oil),
        ("Single Company (1)", f_single),
        ("Empty Dataset (0)", f_zero),
    ]

    for name, test_df in test_datasets:
        # Overview Charts
        fig_rev = analysis.chart_top10_revenue(test_df)
        assert fig_rev is not None
        fig_prof = analysis.chart_top10_profit(test_df)
        assert fig_prof is not None
        fig_c_cnt = analysis.chart_companies_by_country(test_df)
        assert fig_c_cnt is not None
        fig_c_ind = analysis.chart_companies_by_industry(test_df)
        assert fig_c_ind is not None
        fig_rev_c = analysis.chart_revenue_by_country(test_df)
        assert fig_rev_c is not None
        fig_rev_ind = analysis.chart_revenue_by_industry(test_df)
        assert fig_rev_ind is not None

        # Analytics Charts
        fig_rvp = analysis.chart_revenue_vs_profit(test_df)
        assert fig_rvp is not None
        fig_wp = analysis.chart_workforce_productivity(test_df)
        assert fig_wp is not None
        fig_map = analysis.chart_revenue_by_country_map(test_df)
        assert fig_map is not None
        fig_margins = analysis.chart_top_profit_margins(test_df)
        assert fig_margins is not None
        fig_sec_mar = analysis.chart_margin_by_industry(test_df)
        assert fig_sec_mar is not None
        fig_quad = analysis.chart_capital_efficiency_quadrant(test_df)
        assert fig_quad is not None
        fig_pareto = analysis.chart_pareto_revenue_concentration(test_df)
        assert fig_pareto is not None

        # Aggregations & Q&A
        ind_b = analysis.get_industry_benchmarks(test_df)
        assert isinstance(ind_b, pd.DataFrame)
        cntry_b = analysis.get_country_benchmarks(test_df)
        assert isinstance(cntry_b, pd.DataFrame)
        q_ans = analysis.get_business_questions_answers(test_df)
        assert len(q_ans) == 6
        p_stats = analysis.get_revenue_concentration_stats(test_df)
        assert isinstance(p_stats, dict)

        print(f"[PASS] All 15 charts & engines generated cleanly for '{name}'")

    print("\n--- 5. TESTING COMPANY EXPLORER & PRIVATE FIRM EDGE CASE ---")
    # Public company with full data
    prof_amz = analysis.get_company_profile(df, "Amazon")
    assert prof_amz["Company"] == "Amazon"
    fig_amz_bench = analysis.chart_company_profile_benchmark(df, "Amazon")
    assert fig_amz_bench is not None
    print("[PASS] Public Profile (Amazon): OK")

    # Private firm with NaN profit (Schwarz Gruppe)
    prof_schwarz = analysis.get_company_profile(df, "Schwarz Gruppe")
    assert prof_schwarz["Company"] == "Schwarz Gruppe"
    assert prof_schwarz["Profit"] is None
    assert prof_schwarz["Margin"] is None
    fig_schwarz_bench = analysis.chart_company_profile_benchmark(df, "Schwarz Gruppe")
    assert fig_schwarz_bench is not None
    print("[PASS] Private Profile with NaN Profit (Schwarz Gruppe): Handled gracefully without crash")

    print("\n--- 6. TESTING COMPARATOR ---")
    fig_cmp, cmp_table = analysis.compare_companies(df, "Amazon", "Walmart")
    assert fig_cmp is not None
    assert len(cmp_table) == 9
    print("[PASS] Comparison Amazon vs. Walmart: OK")

    fig_cmp2, cmp_table2 = analysis.compare_companies(df, "Schwarz Gruppe", "Apple")
    assert fig_cmp2 is not None
    assert len(cmp_table2) == 9
    print("[PASS] Comparison Private (Schwarz Gruppe) vs. Public (Apple): OK")

    print("\n--- 7. TESTING PHASE 7 BUSINESS QUESTIONS & EXCEL WORKBOOK EXPORT ---")
    from analysis import BUSINESS_QUESTIONS_MAP

    # Verify 10 questions and valid routes
    assert len(BUSINESS_QUESTIONS_MAP) == 10, f"Expected 10 questions, got {len(BUSINESS_QUESTIONS_MAP)}"
    valid_pages = {"Overview", "Analytics", "Business Questions", "Company Explorer", "Compare", "Data"}
    valid_groups = {"FINANCIAL", "GEOGRAPHIC", "INDUSTRY", "EFFICIENCY", "CONCENTRATION"}

    for q_name, q_info in BUSINESS_QUESTIONS_MAP.items():
        assert q_info["page"] in valid_pages, f"Invalid page {q_info['page']} for {q_name}"
        assert q_info["group"] in valid_groups, f"Invalid group {q_info['group']} for {q_name}"
        assert len(q_info["question"]) > 10, f"Empty question text for {q_name}"
        assert len(q_info["target_desc"]) > 5, f"Empty target description for {q_name}"
    print("[PASS] All 10 Business Questions verified with valid groups and target routes.")

    # Verify Excel workbook generation across all filter permutations
    datasets = [
        ("Full 50 Universe", df),
        ("US Only (24 firms)", f_us),
        ("Oil and gas (8 firms)", f_oil),
        ("Single Firm (1 firm)", f_single),
        ("Empty Set (0 firms)", f_zero),
    ]

    for label, sub_df in datasets:
        buf = analysis.generate_excel_export(sub_df, active_filters_desc=label)
        assert buf is not None and len(buf.getvalue()) > 1000, f"Buffer empty for {label}"

        # Load back with openpyxl to verify workbook integrity
        wb = openpyxl.load_workbook(buf)
        sheet_names = wb.sheetnames
        assert "Company Data" in sheet_names, f"Missing Company Data in {label}"
        assert "Executive Summary" in sheet_names, f"Missing Executive Summary in {label}"
        assert "Benchmarks" in sheet_names, f"Missing Benchmarks in {label}"
        assert "Charts" in sheet_names, f"Missing Charts in {label}"

        # Verify Company Data sheet structure
        ws_data = wb["Company Data"]
        assert ws_data["A1"].value == "GLOBAL 50 — CORPORATE INTELLIGENCE"
        assert ws_data.freeze_panes == "A5", f"Expected freeze_panes A5, got {ws_data.freeze_panes}"
        if not sub_df.empty:
            assert len(ws_data.tables) >= 1, f"Missing Excel Table in {label}"

        # Verify Benchmarks sheet
        ws_bench = wb["Benchmarks"]
        if not sub_df.empty:
            assert len(ws_bench.tables) >= 1, f"Missing Benchmark Tables in {label}"

        # Verify Charts sheet
        ws_charts = wb["Charts"]
        if len(sub_df) >= 2:
            assert len(ws_charts._charts) >= 1, f"Missing Excel Charts in {label}"

        print(f"[PASS] Excel workbook verified ({len(buf.getvalue()):,} bytes, 4 sheets) for '{label}'")

    # Verify dynamic filename generator
    fn_full = analysis.get_export_filename()
    assert "all_companies" in fn_full and fn_full.endswith(".xlsx")
    fn_filter = analysis.get_export_filename(countries=["United States"], industries=["Technology"], search="Apple")
    assert "apple" in fn_filter and "United_States" in fn_filter and "filtered" in fn_filter
    print(f"[PASS] Dynamic filenames verified: '{fn_full}', '{fn_filter}'")

    print("\n=======================================================")
    print("ALL PRODUCTION QA CHECKS PASSED WITH ZERO ERRORS!")
    print("=======================================================")


if __name__ == "__main__":
    run_qa_suite()

