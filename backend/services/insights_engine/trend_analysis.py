import pandas as pd

MAX_TREND_POINTS = 365

def apply_date_filters(
    df: pd.DataFrame,
    date_col: str,
    start_date: str = None,
    end_date: str = None
) -> tuple:
    """
    Filters DataFrame by requested date boundaries
    and returns clean dataframe and actual date window.
    """

    actual_start, actual_end = None, None

    if not date_col or len(df) == 0:
        return df, actual_start, actual_end

    try:
        temp_dates = pd.to_datetime(df[date_col], errors='coerce')

        valid_indices = temp_dates.notna()

        if valid_indices.any():

            df = df[valid_indices].copy()

            df[date_col] = temp_dates[valid_indices]

            # Chronological ordering
            df = df.sort_values(by=date_col)

            # Optional filtering
            if start_date:
                df = df[df[date_col] >= pd.to_datetime(start_date)]

            if end_date:
                df = df[df[date_col] <= pd.to_datetime(end_date)]

            # Actual retained interval
            if len(df) > 0:
                actual_start = df[date_col].min().isoformat()
                actual_end = df[date_col].max().isoformat()

    except Exception:
        pass

    return df, actual_start, actual_end


def generate_trends(df: pd.DataFrame, date_col: str) -> tuple:
    """
    Produces trend series for plotting and downstream analytics.
    Limits trend payload size for large enterprise datasets.
    """

    if not date_col or date_col not in df.columns or len(df) == 0:
        return [], None

    try:
        # Aggregate daily ticket counts
        daily_counts = df.groupby(df[date_col].dt.date).size()

        trends_list = [
            {
                "date": str(k),
                "count": int(v)
            }
            for k, v in daily_counts.items()
        ]

        # Retain latest N points only
        trends_list = trends_list[-MAX_TREND_POINTS:]

        return trends_list, daily_counts

    except Exception:
        return [], None