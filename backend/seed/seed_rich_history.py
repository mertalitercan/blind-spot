"""
Seed 100 realistic historical sessions per user (300 total).

User profiles:
- Mertali Tercan: Fast typer (70-85 WPM), reads a lot before big transactions (long screen dwell),
  not hesitant on confirm but spends time reading, occasional typos, tech-savvy, uses biometric,
  consistent device, late-night user, Turkish keyboard quirks.

- Ediz Uysal: Normal baseline. Average typing (38-48 WPM), moderate session times,
  uses both biometric and password, standard navigation patterns, typical business hours,
  occasional clipboard for account numbers, steady hand, no unusual patterns.

- Deniz Coban: Slow typer (14-24 WPM), elderly, hesitant on confirm (long hesitation),
  doesn't read much but navigates slowly, high error rate, uses paste frequently,
  large touch radius, sometimes on phone call during session, charges iPad often,
  morning user, password auth only, occasionally forgets and retries.
"""

import uuid
import random
import math
from datetime import datetime, timedelta


def generate_mertali_sessions(count=100):
    """Fast typer, reads before big txns, occasional mistakes, tech-savvy, night owl."""
    rows = []
    base_date = datetime(2026, 3, 14, 12, 0, 0)

    typical_recipients = ["landlord-utilities", "grocery-store", "spotify", "steam", "contractor-mike-456"]
    typical_hours = [9, 10, 11, 14, 15, 16, 21, 22, 23, 0]  # night owl

    for i in range(count):
        days_ago = i * 0.9 + random.uniform(0, 0.5)  # ~1 session per day, some days 2
        ts = base_date - timedelta(days=days_ago)
        hour = random.choice(typical_hours)
        ts = ts.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        # Amount varies: mostly small (20-300), occasionally big (500-800)
        is_big_txn = random.random() < 0.15
        if is_big_txn:
            amount = round(random.uniform(500, 800), 2)
        else:
            amount = round(random.uniform(20, 300), 2)

        # Typing: fast but with occasional bursts of mistakes
        has_typo_burst = random.random() < 0.12
        typing_speed = random.uniform(70, 85) if not has_typo_burst else random.uniform(60, 75)
        error_rate = random.uniform(0.008, 0.025) if not has_typo_burst else random.uniform(0.04, 0.08)

        # Rhythm: tight, fast intervals with low variance
        base_rhythm = random.uniform(45, 60)
        rhythm = [round(base_rhythm + random.uniform(-8, 8)) for _ in range(10)]

        # Big transactions: spends MORE time reading (longer session, higher screen dwell)
        if is_big_txn:
            session_duration = random.randint(120000, 200000)  # 2-3.3 min — reads carefully
            nav_directness = random.uniform(0.55, 0.75)  # explores more screens
            screen_familiarity = random.uniform(0.75, 0.90)
            confirm_hesitation = random.randint(80, 250)  # NOT hesitant, just reads first
        else:
            session_duration = random.randint(60000, 110000)  # 1-1.8 min — quick
            nav_directness = random.uniform(0.75, 0.92)
            screen_familiarity = random.uniform(0.85, 0.95)
            confirm_hesitation = random.randint(50, 150)

        # Touch: light, precise
        touch_pressure = random.uniform(0.42, 0.54)
        touch_radius = random.uniform(10.5, 12.5)

        # Occasionally uses a different IP (travels within Canada)
        travels = random.random() < 0.08
        if travels:
            ip_city = random.choice(["Montreal", "Ottawa", "Vancouver"])
            ip_lat = {"Montreal": 45.50, "Ottawa": 45.42, "Vancouver": 49.28}[ip_city]
            ip_lng = {"Montreal": -73.57, "Ottawa": -75.69, "Vancouver": -123.12}[ip_city]
            ip_addr = f"24.{random.randint(100,200)}.{random.randint(1,254)}.{random.randint(1,254)}"
        else:
            ip_city = "Toronto"
            ip_lat = round(43.65 + random.uniform(-0.04, 0.04), 4)
            ip_lng = round(-79.38 + random.uniform(-0.04, 0.04), 4)
            ip_addr = f"24.114.{random.randint(1,254)}.{random.randint(1,254)}"

        # Never on phone during banking, no paste, no segmented typing
        rows.append({
            "user_id": "mertali-tercan",
            "session_id": str(uuid.uuid4()),
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "typing_speed_wpm": round(typing_speed, 1),
            "error_rate": round(error_rate, 4),
            "typing_rhythm_signature": rhythm,
            "avg_touch_pressure": round(touch_pressure, 3),
            "avg_touch_radius": round(touch_radius, 2),
            "hand_dominance": "right",
            "navigation_directness_score": round(nav_directness, 3),
            "screen_familiarity_score": round(screen_familiarity, 3),
            "session_duration_ms": session_duration,
            "segmented_typing_detected": False,
            "paste_detected": False,
            "paste_field": "",
            "confirm_button_hesitation_ms": confirm_hesitation,
            "confirm_attempts": 1,
            "total_dead_time_ms": 0,
            "ip_address": ip_addr,
            "ip_city": ip_city,
            "ip_country": "CA",
            "ip_lat": ip_lat,
            "ip_lng": ip_lng,
            "device_id": "iPhone-16-Pro-MT001",
            "auth_method": "biometric",  # always biometric — tech savvy
            "transaction_amount": amount,
            "recipient_account_id": random.choice(typical_recipients),
            "recipient_name": "",
            "fraud_score": random.randint(0, 8),
        })

    return rows


def generate_ediz_sessions(count=100):
    """Normal user. Average everything. Consistent, unremarkable patterns."""
    rows = []
    base_date = datetime(2026, 3, 14, 12, 0, 0)

    typical_recipients = ["landlord-utilities", "grocery-store", "pharmacy", "netflix", "friend-alex-890"]
    typical_hours = [8, 9, 10, 12, 13, 17, 18, 19]

    for i in range(count):
        days_ago = i * 0.95 + random.uniform(0, 0.6)
        ts = base_date - timedelta(days=days_ago)
        hour = random.choice(typical_hours)
        ts = ts.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        amount = round(random.uniform(30, 500), 2)

        typing_speed = random.uniform(38, 48)
        error_rate = random.uniform(0.03, 0.06)

        # Rhythm: moderate intervals with normal variance
        base_rhythm = random.uniform(90, 115)
        rhythm = [round(base_rhythm + random.uniform(-15, 15)) for _ in range(10)]

        session_duration = random.randint(140000, 220000)  # 2.3-3.7 min
        nav_directness = random.uniform(0.35, 0.55)
        screen_familiarity = random.uniform(0.55, 0.75)
        confirm_hesitation = random.randint(200, 900)

        touch_pressure = random.uniform(0.46, 0.56)
        touch_radius = random.uniform(12.0, 14.5)

        # Sometimes uses clipboard for account numbers (20% of time)
        uses_clipboard = random.random() < 0.20

        # Occasionally uses password instead of biometric (30%)
        auth = "password" if random.random() < 0.30 else "biometric"

        ip_addr = f"72.38.{random.randint(1,254)}.{random.randint(1,254)}"

        # Rarely on phone (5% — normal calls, not suspicious)
        on_phone = random.random() < 0.05

        # Sometimes has dead time — thinking/distracted (15%)
        has_dead_time = random.random() < 0.15
        dead_time = random.randint(5000, 12000) if has_dead_time else 0

        rows.append({
            "user_id": "ediz-uysal",
            "session_id": str(uuid.uuid4()),
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "typing_speed_wpm": round(typing_speed, 1),
            "error_rate": round(error_rate, 4),
            "typing_rhythm_signature": rhythm,
            "avg_touch_pressure": round(touch_pressure, 3),
            "avg_touch_radius": round(touch_radius, 2),
            "hand_dominance": "right",
            "navigation_directness_score": round(nav_directness, 3),
            "screen_familiarity_score": round(screen_familiarity, 3),
            "session_duration_ms": session_duration,
            "segmented_typing_detected": False,
            "paste_detected": uses_clipboard,
            "paste_field": "recipient_account" if uses_clipboard else "",
            "confirm_button_hesitation_ms": confirm_hesitation,
            "confirm_attempts": 1,
            "total_dead_time_ms": dead_time,
            "ip_address": ip_addr,
            "ip_city": "Toronto",
            "ip_country": "CA",
            "ip_lat": round(43.65 + random.uniform(-0.04, 0.04), 4),
            "ip_lng": round(-79.38 + random.uniform(-0.04, 0.04), 4),
            "device_id": "Galaxy-S24-EU002",
            "auth_method": auth,
            "transaction_amount": amount,
            "recipient_account_id": random.choice(typical_recipients),
            "recipient_name": "",
            "fraud_score": random.randint(0, 12),
        })

    return rows


def generate_deniz_sessions(count=100):
    """Slow typer, elderly, hesitant, high error rate, uses paste a lot,
    large touch radius, sometimes on phone, morning user, iPad, password only,
    occasionally retries confirm, opposite of Mertali in every way."""
    rows = []
    base_date = datetime(2026, 3, 14, 12, 0, 0)

    typical_recipients = ["landlord-utilities", "pharmacy", "grocery-store"]
    typical_hours = [9, 10, 11, 14, 15]  # morning/early afternoon only

    for i in range(count):
        days_ago = i * 1.2 + random.uniform(0, 0.8)  # less frequent than others
        ts = base_date - timedelta(days=days_ago)
        hour = random.choice(typical_hours)
        ts = ts.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        # Small transactions mostly — pension, groceries, pharmacy
        amount = round(random.uniform(15, 200), 2)

        # Very slow typing with high variance
        typing_speed = random.uniform(14, 24)
        error_rate = random.uniform(0.08, 0.16)

        # Rhythm: very slow intervals, high variance (inconsistent)
        base_rhythm = random.uniform(260, 340)
        rhythm = [round(base_rhythm + random.uniform(-40, 40)) for _ in range(10)]

        # Long sessions — she's slow at everything
        session_duration = random.randint(300000, 500000)  # 5-8 min
        nav_directness = random.uniform(0.15, 0.30)  # wanders, clicks wrong things
        screen_familiarity = random.uniform(0.20, 0.45)

        # VERY hesitant on confirm — reads, re-reads, sometimes retries
        retries_confirm = random.random() < 0.25
        confirm_hesitation = random.randint(2000, 6000)
        confirm_attempts = random.choice([2, 3]) if retries_confirm else 1

        # Heavy touch, large radius (less precise)
        touch_pressure = random.uniform(0.58, 0.72)
        touch_radius = random.uniform(15.0, 18.5)

        # Uses paste frequently (60%) — copies amounts and account info
        uses_paste = random.random() < 0.60
        paste_field = random.choice(["amount", "recipient_account"]) if uses_paste else ""

        # Sometimes on phone (15%) — calls family for help with banking
        on_phone = random.random() < 0.15
        phone_duration = random.randint(60000, 300000) if on_phone else 0

        # Dead time frequent (40%) — pauses to think, read glasses, etc.
        has_dead_time = random.random() < 0.40
        dead_time = random.randint(8000, 25000) if has_dead_time else 0

        # Always same IP, same device, always password (doesn't trust biometric)
        ip_addr = f"99.225.{random.randint(80,95)}.{random.randint(1,254)}"

        # Occasionally segmented typing (20%) — types digit by digit slowly
        segmented = random.random() < 0.20

        rows.append({
            "user_id": "deniz-coban",
            "session_id": str(uuid.uuid4()),
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "typing_speed_wpm": round(typing_speed, 1),
            "error_rate": round(error_rate, 4),
            "typing_rhythm_signature": rhythm,
            "avg_touch_pressure": round(touch_pressure, 3),
            "avg_touch_radius": round(touch_radius, 2),
            "hand_dominance": "right",
            "navigation_directness_score": round(nav_directness, 3),
            "screen_familiarity_score": round(screen_familiarity, 3),
            "session_duration_ms": session_duration,
            "segmented_typing_detected": segmented,
            "paste_detected": uses_paste,
            "paste_field": paste_field,
            "confirm_button_hesitation_ms": confirm_hesitation,
            "confirm_attempts": confirm_attempts,
            "total_dead_time_ms": dead_time,
            "ip_address": ip_addr,
            "ip_city": "Toronto",
            "ip_country": "CA",
            "ip_lat": round(43.70 + random.uniform(-0.03, 0.03), 4),
            "ip_lng": round(-79.42 + random.uniform(-0.03, 0.03), 4),
            "device_id": "iPad-Air-DC003",
            "auth_method": "password",  # never uses biometric
            "transaction_amount": amount,
            "recipient_account_id": random.choice(typical_recipients),
            "recipient_name": "",
            "fraud_score": random.randint(0, 10),
        })

    return rows


def seed_all():
    from database import supabase, clear_all_sessions

    print("Clearing existing sessions...")
    clear_all_sessions()

    print("Generating Mertali sessions (100)...")
    mertali = generate_mertali_sessions(100)

    print("Generating Ediz sessions (100)...")
    ediz = generate_ediz_sessions(100)

    print("Generating Deniz sessions (100)...")
    deniz = generate_deniz_sessions(100)

    all_rows = mertali + ediz + deniz
    random.shuffle(all_rows)

    print(f"Inserting {len(all_rows)} rows into Supabase...")
    batch_size = 50
    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i:i+batch_size]
        supabase.table("session_history").insert(batch).execute()
        print(f"  Inserted batch {i//batch_size + 1}/{math.ceil(len(all_rows)/batch_size)}")

    print("Done! Seeded 300 sessions (100 per user)")

    # Print summary stats
    for name, sessions in [("Mertali", mertali), ("Ediz", ediz), ("Deniz", deniz)]:
        speeds = [s["typing_speed_wpm"] for s in sessions]
        errors = [s["error_rate"] for s in sessions]
        hesitations = [s["confirm_button_hesitation_ms"] for s in sessions]
        amounts = [s["transaction_amount"] for s in sessions]
        pastes = sum(1 for s in sessions if s["paste_detected"])
        print(f"\n  {name}:")
        print(f"    Speed: {min(speeds):.0f}-{max(speeds):.0f} WPM (avg {sum(speeds)/len(speeds):.1f})")
        print(f"    Error rate: {min(errors):.3f}-{max(errors):.3f}")
        print(f"    Confirm hesitation: {min(hesitations)}-{max(hesitations)} ms")
        print(f"    Amount range: ${min(amounts):.0f}-${max(amounts):.0f}")
        print(f"    Paste usage: {pastes}/{len(sessions)} sessions")


if __name__ == "__main__":
    seed_all()
