import pandas as pd
from config import SPIKE_WINDOW_DAYS

def detect_spikes(daily_counts, window_size=None):
    """
    Detect abnormal ticket spikes using rolling statistical thresholds.
    Falls back to config.SPIKE_WINDOW_DAYS if not provided.
    """
    # Determine active window
    effective_window = int(window_size) if window_size is not None else SPIKE_WINDOW_DAYS

    spikes = []

    if daily_counts is None or len(daily_counts) < 3:
        return spikes

    rolling_mean = daily_counts.rolling(
        window=effective_window,
        min_periods=1
    ).mean()

    rolling_std = daily_counts.rolling(
        window=effective_window,
        min_periods=1
    ).std().fillna(0)

    threshold = rolling_mean + (1.5 * rolling_std)

    avg_daily = daily_counts.mean()

    for date_obj, count in daily_counts.items():

        if count > threshold.loc[date_obj] and count > avg_daily:

            pct_above = (
                round(((count - avg_daily) / avg_daily) * 100, 1)
                if avg_daily > 0 else 100.0
            )

            spikes.append({
                "date": str(date_obj),
                "count": int(count),
                "percentage_above_avg": pct_above,
                "rolling_window_days": effective_window
            })

    return spikes