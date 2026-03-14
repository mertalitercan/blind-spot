import json
import math
import railtracks as rt


@rt.function_node
def compute_transaction_features(transaction_json: str, history_json: str) -> str:
    """Compute transaction anomaly features by comparing current transaction to user history. Returns JSON."""
    tx = json.loads(transaction_json)
    history = json.loads(history_json)

    amount = tx.get("amount", 0)
    avg_30d = history.get("rolling_avg_amount_30d", 0)
    max_90d = history.get("max_amount_90d", 0)
    std_dev = history.get("std_dev_amount_30d", avg_30d * 0.5) if avg_30d > 0 else 1

    amount_zscore = round((amount - avg_30d) / std_dev, 2) if std_dev > 0 else 0
    amount_ratio_avg = round(amount / avg_30d, 2) if avg_30d > 0 else 0
    amount_ratio_max = round(amount / max_90d, 2) if max_90d > 0 else 0

    recipient_id = tx.get("recipient_account_id", "")
    known_recipients = history.get("typical_recipients", [])
    is_new_recipient = recipient_id not in known_recipients

    is_round = amount == round(amount, -1) or amount == round(amount, -2)

    timestamp = tx.get("timestamp", "")
    hour = 12
    if "T" in timestamp:
        try:
            hour = int(timestamp.split("T")[1][:2])
        except (ValueError, IndexError):
            hour = 12

    typical_times = history.get("typical_transaction_times", [])
    time_anomaly = True
    for time_range in typical_times:
        if "-" in time_range:
            parts = time_range.split("-")
            start_h = int(parts[0].split(":")[0])
            end_h = int(parts[1].split(":")[0])
            if start_h <= hour <= end_h:
                time_anomaly = False
                break

    if hour < 6:
        time_bucket = "night_0_6"
    elif hour < 12:
        time_bucket = "morning_6_12"
    elif hour < 18:
        time_bucket = "afternoon_12_18"
    else:
        time_bucket = "evening_18_24"

    return json.dumps({
        "amount_zscore": amount_zscore,
        "amount_ratio_avg_30d": amount_ratio_avg,
        "amount_ratio_max_90d": amount_ratio_max,
        "is_new_recipient": is_new_recipient,
        "is_round_number": is_round,
        "time_of_day_bucket": time_bucket,
        "hour": hour,
        "time_anomaly": time_anomaly,
        "exceeds_90d_max": amount > max_90d,
    })
