import json
import math
import railtracks as rt


@rt.function_node
def compute_typing_features(keystroke_events_json: str) -> str:
    """Extract typing rhythm features from keystroke event data. Returns JSON with computed features."""
    events = json.loads(keystroke_events_json)
    if not events:
        return json.dumps({"typing_speed_wpm": 0, "avg_dwell_time_ms": 0, "avg_flight_time_ms": 0, "rhythm_signature": []})

    dwell_times = [e.get("dwell_time_ms", 0) for e in events]
    flight_times = [e.get("flight_time_ms", 0) for e in events]
    timestamps = [e.get("timestamp_ms", 0) for e in events]

    total_time_s = (timestamps[-1] - timestamps[0]) / 1000.0 if len(timestamps) > 1 else 1.0
    words_approx = len(events) / 5.0
    typing_speed = (words_approx / total_time_s) * 60 if total_time_s > 0 else 0

    return json.dumps({
        "typing_speed_wpm": round(typing_speed, 1),
        "avg_dwell_time_ms": round(sum(dwell_times) / len(dwell_times), 1) if dwell_times else 0,
        "avg_flight_time_ms": round(sum(flight_times) / len(flight_times), 1) if flight_times else 0,
        "rhythm_signature": flight_times[:20],
    })


@rt.function_node
def compare_to_baseline(current_features_json: str, baseline_json: str) -> str:
    """Compare current behavioral features against user baseline. Returns JSON with deviation ratios."""
    current = json.loads(current_features_json)
    baseline = json.loads(baseline_json)

    def safe_ratio(current_val: float, baseline_val: float) -> float:
        if baseline_val == 0:
            return 1.0
        return round(current_val / baseline_val, 2)

    typing_speed_ratio = safe_ratio(
        current.get("typing_speed_wpm", 0),
        baseline.get("avg_typing_speed_wpm", 40)
    )
    error_rate_ratio = safe_ratio(
        current.get("error_rate", 0),
        baseline.get("typical_error_rate", 0.05)
    )
    touch_pressure_ratio = safe_ratio(
        current.get("avg_touch_pressure", 0.5),
        baseline.get("avg_touch_pressure", 0.5)
    )
    session_duration_ratio = safe_ratio(
        current.get("session_duration_ms", 0),
        baseline.get("avg_session_duration_ms", 180000)
    )
    directness_current = current.get("navigation_directness_score", 0.5)
    directness_baseline = baseline.get("typical_navigation_directness", 0.35)

    return json.dumps({
        "typing_speed_ratio": typing_speed_ratio,
        "error_rate_ratio": error_rate_ratio,
        "touch_pressure_ratio": touch_pressure_ratio,
        "session_duration_ratio": session_duration_ratio,
        "navigation_directness_current": directness_current,
        "navigation_directness_baseline": directness_baseline,
        "directness_deviation": round(abs(directness_current - directness_baseline), 2),
    })


def compute_rhythm_distance(sig_a: list[float], sig_b: list[float]) -> float:
    """Simplified DTW-like distance between two rhythm signatures."""
    if not sig_a or not sig_b:
        return 0.0
    min_len = min(len(sig_a), len(sig_b))
    sig_a = sig_a[:min_len]
    sig_b = sig_b[:min_len]
    diffs = [(a - b) ** 2 for a, b in zip(sig_a, sig_b)]
    return round(math.sqrt(sum(diffs) / len(diffs)), 2)
