"""Supabase session database — stores behavioral session data for historical comparison."""

import json
import uuid
import os
import random
from datetime import datetime

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_session(user_id: str, transaction_data: dict, fraud_score: int = 0):
    """Save a session's behavioral data to Supabase for future comparison."""
    telemetry = transaction_data.get("behavioral_telemetry", {})
    geo = transaction_data.get("ip_geolocation", {})
    device_fp = transaction_data.get("device_fingerprint", {})
    nav_path = telemetry.get("navigation_path", [])
    session_duration = sum(s.get("duration_ms", 0) for s in nav_path)

    row = {
        "user_id": user_id,
        "session_id": transaction_data.get("session_id", str(uuid.uuid4())),
        "timestamp": transaction_data.get("timestamp", datetime.utcnow().isoformat()),
        "typing_speed_wpm": telemetry.get("typing_speed_wpm", 0),
        "error_rate": telemetry.get("error_rate", 0),
        "typing_rhythm_signature": telemetry.get("typing_rhythm_signature", []),
        "avg_touch_pressure": telemetry.get("avg_touch_pressure", 0),
        "avg_touch_radius": telemetry.get("avg_touch_radius", 0),
        "hand_dominance": telemetry.get("hand_dominance", "unknown"),
        "navigation_directness_score": telemetry.get("navigation_directness_score", 0),
        "screen_familiarity_score": telemetry.get("screen_familiarity_score", 0),
        "session_duration_ms": session_duration,
        "segmented_typing_detected": telemetry.get("segmented_typing_detected", False),
        "paste_detected": telemetry.get("paste_detected", False),
        "paste_field": telemetry.get("paste_field", ""),
        "confirm_button_hesitation_ms": telemetry.get("confirm_button_hesitation_ms", 0),
        "confirm_attempts": telemetry.get("confirm_attempts", 1),
        "total_dead_time_ms": telemetry.get("total_dead_time_ms", 0),
        "ip_address": transaction_data.get("ip_address", ""),
        "ip_city": geo.get("city", ""),
        "ip_country": geo.get("country", ""),
        "ip_lat": geo.get("lat", 0),
        "ip_lng": geo.get("lng", 0),
        "device_id": device_fp.get("device_id", ""),
        "auth_method": transaction_data.get("auth_method", ""),
        "transaction_amount": transaction_data.get("amount", 0),
        "recipient_account_id": transaction_data.get("recipient_account_id", ""),
        "recipient_name": transaction_data.get("recipient_name", ""),
        "fraud_score": fraud_score,
    }

    supabase.table("session_history").insert(row).execute()


def get_user_sessions(user_id: str, limit: int = 20) -> list[dict]:
    """Get the most recent sessions for a user."""
    result = (
        supabase.table("session_history")
        .select("*")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def get_user_ip_history(user_id: str) -> list[dict]:
    """Get all sessions for a user to compute IP history."""
    result = (
        supabase.table("session_history")
        .select("ip_address, ip_city, ip_country, ip_lat, ip_lng, timestamp")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .execute()
    )
    # Aggregate by IP
    ip_map = {}
    for row in result.data:
        ip = row.get("ip_address", "")
        if ip not in ip_map:
            ip_map[ip] = {
                "ip_address": ip,
                "ip_city": row.get("ip_city", ""),
                "ip_country": row.get("ip_country", ""),
                "ip_lat": row.get("ip_lat", 0),
                "ip_lng": row.get("ip_lng", 0),
                "login_count": 0,
                "last_seen": row.get("timestamp", ""),
            }
        ip_map[ip]["login_count"] += 1
    return sorted(ip_map.values(), key=lambda x: x["login_count"], reverse=True)


def get_user_device_history(user_id: str) -> list[dict]:
    """Get unique devices used by a user."""
    result = (
        supabase.table("session_history")
        .select("device_id, timestamp")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .execute()
    )
    device_map = {}
    for row in result.data:
        did = row.get("device_id", "")
        if did not in device_map:
            device_map[did] = {"device_id": did, "usage_count": 0, "last_seen": row.get("timestamp", "")}
        device_map[did]["usage_count"] += 1
    return sorted(device_map.values(), key=lambda x: x["usage_count"], reverse=True)


def clear_all_sessions():
    """Delete all rows from session_history."""
    # Supabase requires a filter for delete; use a always-true condition
    supabase.table("session_history").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()


def seed_historical_sessions(force: bool = False):
    """Seed historical session data for demo users so agents have history to compare against."""
    from seed.seed_scenarios import USER_BASELINES

    # Check if already seeded (skip unless forced)
    if not force:
        result = supabase.table("session_history").select("id").limit(1).execute()
        if result.data:
            return

    rows = []
    for user_id, baseline in USER_BASELINES.items():
        base_speed = baseline["avg_typing_speed_wpm"]
        base_pressure = baseline["avg_touch_pressure"]
        base_radius = baseline["avg_touch_radius"]
        base_directness = baseline["typical_navigation_directness"]
        base_error = baseline["typical_error_rate"]
        base_duration = baseline["avg_session_duration_ms"]
        base_rhythm = baseline["typing_rhythm_signature"]
        known_device = baseline["known_devices"][0]
        ip_prefix = baseline["typical_ip_range"].replace("x.x", "")

        for day_offset in range(15):
            hour = random.choice(baseline["typical_login_hours"])
            day = max(1, 14 - (day_offset % 28))
            month = 3 if day_offset < 14 else 2
            timestamp = f"2026-{month:02d}-{day:02d}T{hour:02d}:{random.randint(0,59):02d}:00Z"

            jitter = lambda v, pct=0.15: round(v * random.uniform(1 - pct, 1 + pct), 3)
            rhythm_jittered = [round(r * random.uniform(0.85, 1.15)) for r in base_rhythm]

            rows.append({
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "timestamp": timestamp,
                "typing_speed_wpm": jitter(base_speed),
                "error_rate": jitter(base_error, 0.3),
                "typing_rhythm_signature": rhythm_jittered,
                "avg_touch_pressure": jitter(base_pressure),
                "avg_touch_radius": jitter(base_radius),
                "hand_dominance": baseline["hand_dominance"],
                "navigation_directness_score": jitter(base_directness, 0.2),
                "screen_familiarity_score": round(random.uniform(0.6, 0.9), 3),
                "session_duration_ms": int(jitter(base_duration, 0.3)),
                "segmented_typing_detected": False,
                "paste_detected": baseline.get("paste_frequency") == "high" and random.random() < 0.6,
                "paste_field": "amount" if baseline.get("paste_frequency") == "high" and random.random() < 0.4 else "",
                "confirm_button_hesitation_ms": random.randint(100, 500),
                "confirm_attempts": 1,
                "total_dead_time_ms": 0,
                "ip_address": f"{ip_prefix}{random.randint(1,254)}.{random.randint(1,254)}",
                "ip_city": "Toronto",
                "ip_country": "CA",
                "ip_lat": round(43.65 + random.uniform(-0.05, 0.05), 4),
                "ip_lng": round(-79.38 + random.uniform(-0.05, 0.05), 4),
                "device_id": known_device,
                "auth_method": random.choice(["biometric", "biometric", "password"]),
                "transaction_amount": round(random.uniform(20, 500), 2),
                "recipient_account_id": random.choice(baseline["transaction_history"]["typical_recipients"]),
                "recipient_name": "",
                "fraud_score": random.randint(0, 15),
            })

    # Insert in batches
    for i in range(0, len(rows), 20):
        supabase.table("session_history").insert(rows[i:i+20]).execute()


def init_db():
    """No-op for Supabase — table is created via dashboard SQL editor."""
    pass
