import pandas as pd

from .schema_resolver import resolve_columns
from .trend_analysis import apply_date_filters, generate_trends
from .anomaly_detection import detect_spikes
from .aggregations import (
    calculate_distributions,
    calculate_resolution_performance
)
from .problem_detection import detect_recurring_problems
from .sla_metrics import (
    check_sla_breaches,
    check_reopens
)

# Hard safeguard for oversized enterprise datasets
MAX_ANALYSIS_ROWS = 100000


def run_pipeline(
    df: pd.DataFrame,
    mapping: dict = None,
    start_date: str = None,
    end_date: str = None
) -> dict:
    """
    Sequentially routes DataFrame across
    sub-engine solvers to compile final insights report.
    """

    # 1. Standardize structural definitions
    cols = resolve_columns(df, mapping)

    # 2. Apply timeframe filtering
    df_filtered, s_start, s_end = apply_date_filters(
        df,
        cols.get("date"),
        start_date,
        end_date
    )

    # 3. Prevent extreme memory pressure
    if len(df_filtered) > MAX_ANALYSIS_ROWS:
        df_filtered = df_filtered.tail(MAX_ANALYSIS_ROWS)

    insights = {
        "total_tickets": len(df_filtered),

        "analysis_interval": {
            "start": s_start,
            "end": s_end
        },

        "categories": {},
        "subcategories": {},
        "assignment_groups": {},
        "priority_distribution": {},
        "priority_vs_resolution_time": {},

        "trends": [],

        "spikes_7d": [],
        "spikes_30d": [],

        "problem_candidates": []
    }

    # Empty dataset protection
    if len(df_filtered) == 0:
        return insights

    # -------------------------------------------------
    # 4. Static Distribution Analytics
    # -------------------------------------------------

    dists = calculate_distributions(df_filtered, cols)

    insights.update(dists)

    insights["priority_vs_resolution_time"] = (
        calculate_resolution_performance(
            df_filtered,
            cols.get("priority"),
            cols.get("resolution")
        )
    )

    # -------------------------------------------------
    # 5. Trend & Spike Analytics
    # -------------------------------------------------

    trends, raw_series = generate_trends(
        df_filtered,
        cols.get("date")
    )

    insights["trends"] = trends

    # 7-Day rolling anomaly detection
    insights["spikes_7d"] = detect_spikes(
        raw_series,
        window_size=7
    )

    # 30-Day rolling anomaly detection
    insights["spikes_30d"] = detect_spikes(
        raw_series,
        window_size=30
    )

    # -------------------------------------------------
    # 6. Recurring Problem Detection
    # -------------------------------------------------

    recurring = detect_recurring_problems(
        df_filtered,
        cols.get("description"),
        cols.get("priority"),
        cols.get("sla_breach")
    )

    insights["problem_candidates"].extend(recurring)

    # -------------------------------------------------
    # 7. SLA Risk Aggregation
    # -------------------------------------------------

    sla_issues = check_sla_breaches(
        df_filtered,
        cols.get("sla_breach"),
        cols.get("category")
    )

    insights["problem_candidates"].extend(sla_issues)

    # -------------------------------------------------
    # 8. Reopen Stability Analysis
    # -------------------------------------------------

    reopen_issues = check_reopens(
        df_filtered,
        cols.get("reopen")
    )

    insights["problem_candidates"].extend(reopen_issues)

    # -------------------------------------------------
    # 9. Final Candidate Cap
    # -------------------------------------------------

    insights["problem_candidates"] = (
        insights["problem_candidates"][:8]
    )

    return insights