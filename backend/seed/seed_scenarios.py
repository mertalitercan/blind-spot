"""Pre-built demo scenarios with fully synthetic data for testing the agent pipeline."""

import math

# --- Sender/Recipient business profiles for contextual transaction analysis ---

SENDER_PROFILES = {
    "mertali-tercan": {
        "account_type": "personal",
        "occupation": "Software Engineer",
        "employer": "Shopify",
        "industry": "technology",
        "account_age_days": 1825,
        "typical_location": {"city": "Toronto", "country": "CA", "lat": 43.65, "lng": -79.38},
        "monthly_income_range": "5000-8000",
    },
    "ediz-uysal": {
        "account_type": "personal",
        "occupation": "Marketing Manager",
        "employer": "TD Bank",
        "industry": "finance",
        "account_age_days": 2555,
        "typical_location": {"city": "Toronto", "country": "CA", "lat": 43.65, "lng": -79.38},
        "monthly_income_range": "6000-9000",
    },
    "deniz-coban": {
        "account_type": "personal",
        "occupation": "Retired Teacher",
        "employer": "Retired",
        "industry": "education",
        "account_age_days": 5475,
        "typical_location": {"city": "Toronto", "country": "CA", "lat": 43.70, "lng": -79.42},
        "monthly_income_range": "2500-3500",
    },
}

RECIPIENT_PROFILES_BUSINESS = {
    "landlord-utilities": {
        "business_name": "Toronto Utilities Corp",
        "business_type": "utility_company",
        "industry": "utilities",
        "mcc_code": "4900",
        "mcc_description": "Utilities - Electric, Gas, Sanitary, Water",
        "registered_address": "100 Queen St W, Toronto, ON",
        "years_in_business": 45,
        "website": "torontoutilities.ca",
    },
    "NEW-MULE-ACCOUNT-789": {
        "business_name": "John Smith",
        "business_type": "personal",
        "industry": "unknown",
        "mcc_code": None,
        "mcc_description": "Personal transfer - no merchant category",
        "registered_address": None,
        "years_in_business": 0,
        "website": None,
    },
    "NEW-RECIPIENT-ATO-456": {
        "business_name": "Quick Cash Ltd",
        "business_type": "money_service_business",
        "industry": "financial_services",
        "mcc_code": "6051",
        "mcc_description": "Non-Financial Institutions - Foreign Currency, Money Orders",
        "registered_address": "Unit 12, 455 Spadina Ave, Toronto, ON",
        "years_in_business": 0,
        "website": None,
    },
    "EXTERNAL-MULE-OUT-111": {
        "business_name": "Offshore Holdings Ltd",
        "business_type": "holding_company",
        "industry": "financial_services",
        "mcc_code": "6211",
        "mcc_description": "Security Brokers/Dealers",
        "registered_address": None,
        "years_in_business": 0,
        "website": None,
    },
    "grocery-store": {
        "business_name": "Loblaws",
        "business_type": "grocery",
        "industry": "retail",
        "mcc_code": "5411",
        "mcc_description": "Grocery Stores, Supermarkets",
        "registered_address": "1 President's Choice Circle, Brampton, ON",
        "years_in_business": 105,
        "website": "loblaws.ca",
    },
    "pharmacy": {
        "business_name": "Shoppers Drug Mart",
        "business_type": "pharmacy",
        "industry": "healthcare_retail",
        "mcc_code": "5912",
        "mcc_description": "Drug Stores and Pharmacies",
        "registered_address": "243 Consumers Rd, Toronto, ON",
        "years_in_business": 62,
        "website": "shoppersdrugmart.ca",
    },
}


def compute_geo_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance between two coordinates in km."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─────────────────────────────────────────────────────────────────────────────
# USER BASELINES
# ─────────────────────────────────────────────────────────────────────────────

USER_BASELINES = {
    # ── Mertali Tercan ── Fast typer, Turkish keyboard, very few mistakes, tech-savvy
    "mertali-tercan": {
        "user_id": "mertali-tercan",
        "name": "Mertali Tercan",
        "avg_typing_speed_wpm": 78.5,
        "typing_rhythm_signature": [55, 48, 52, 45, 50, 42, 58, 44, 47, 53],
        "avg_touch_pressure": 0.48,
        "avg_touch_radius": 11.5,
        "hand_dominance": "right",
        "avg_session_duration_ms": 95000,
        "typical_navigation_directness": 0.80,
        "typical_login_hours": [9, 10, 11, 14, 15, 16, 21, 22, 23],
        "typical_error_rate": 0.015,
        "known_devices": ["iPhone-16-Pro-MT001"],
        "typical_ip_range": "24.114.x.x",
        "typical_timezone": "America/Toronto",
        "keyboard_layout": "Turkish-Q",
        "frequent_special_chars": ["ş", "ğ", "ü", "ö", "ç", "ı"],
        "transaction_history": {
            "rolling_avg_amount_30d": 185.00,
            "max_amount_90d": 650.00,
            "std_dev_amount_30d": 110.0,
            "typical_recipients": ["landlord-utilities", "grocery-store", "spotify", "steam"],
            "typical_transaction_times": ["09:00-11:00", "14:00-16:00", "21:00-23:00"],
            "transaction_count_30d": 22,
        },
    },

    # ── Ediz Uysal ── Classic normal user, average everything
    "ediz-uysal": {
        "user_id": "ediz-uysal",
        "name": "Ediz Uysal",
        "avg_typing_speed_wpm": 42.0,
        "typing_rhythm_signature": [115, 88, 95, 108, 90, 92, 105, 98, 87, 110],
        "avg_touch_pressure": 0.50,
        "avg_touch_radius": 13.0,
        "hand_dominance": "right",
        "avg_session_duration_ms": 180000,
        "typical_navigation_directness": 0.40,
        "typical_login_hours": [8, 9, 10, 12, 13, 17, 18, 19],
        "typical_error_rate": 0.045,
        "known_devices": ["Galaxy-S24-EU002"],
        "typical_ip_range": "72.38.x.x",
        "typical_timezone": "America/Toronto",
        "keyboard_layout": "English-QWERTY",
        "frequent_special_chars": [],
        "transaction_history": {
            "rolling_avg_amount_30d": 310.00,
            "max_amount_90d": 800.00,
            "std_dev_amount_30d": 175.0,
            "typical_recipients": ["landlord-utilities", "grocery-store", "pharmacy", "netflix"],
            "typical_transaction_times": ["08:00-10:00", "12:00-13:00", "17:00-19:00"],
            "transaction_count_30d": 20,
        },
    },

    # ── Deniz Coban ── Slow typer, elderly, uses copy-paste a lot, cautious
    "deniz-coban": {
        "user_id": "deniz-coban",
        "name": "Deniz Coban",
        "avg_typing_speed_wpm": 18.5,
        "typing_rhythm_signature": [280, 320, 295, 310, 340, 275, 330, 300, 315, 290],
        "avg_touch_pressure": 0.65,
        "avg_touch_radius": 16.5,
        "hand_dominance": "right",
        "avg_session_duration_ms": 420000,
        "typical_navigation_directness": 0.20,
        "typical_login_hours": [9, 10, 11, 14, 15],
        "typical_error_rate": 0.12,
        "known_devices": ["iPad-Air-DC003"],
        "typical_ip_range": "99.225.x.x",
        "typical_timezone": "America/Toronto",
        "keyboard_layout": "English-QWERTY",
        "frequent_special_chars": [],
        "paste_frequency": "high",
        "transaction_history": {
            "rolling_avg_amount_30d": 95.00,
            "max_amount_90d": 350.00,
            "std_dev_amount_30d": 65.0,
            "typical_recipients": ["landlord-utilities", "pharmacy", "grocery-store"],
            "typical_transaction_times": ["09:00-11:00", "14:00-15:00"],
            "transaction_count_30d": 8,
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# RECIPIENT GRAPH DATA
# ─────────────────────────────────────────────────────────────────────────────

RECIPIENT_GRAPH_DATA = {
    "landlord-utilities": {
        "account_id": "landlord-utilities",
        "account_name": "Toronto Utilities Corp",
        "incoming_transfers_24h": 0,
        "unique_senders_24h": 0,
        "avg_sender_account_age_days": 1000,
        "all_senders_first_time": False,
        "recipient_account_age_days": 2500,
        "flagged": False,
    },
    "grocery-store": {
        "account_id": "grocery-store",
        "account_name": "Loblaws",
        "incoming_transfers_24h": 0,
        "unique_senders_24h": 0,
        "avg_sender_account_age_days": 800,
        "all_senders_first_time": False,
        "recipient_account_age_days": 5000,
        "flagged": False,
    },
    "pharmacy": {
        "account_id": "pharmacy",
        "account_name": "Shoppers Drug Mart",
        "incoming_transfers_24h": 0,
        "unique_senders_24h": 0,
        "avg_sender_account_age_days": 900,
        "all_senders_first_time": False,
        "recipient_account_age_days": 4000,
        "flagged": False,
    },
    "NEW-MULE-ACCOUNT-789": {
        "account_id": "NEW-MULE-ACCOUNT-789",
        "account_name": "John Smith",
        "incoming_transfers_24h": 4,
        "unique_senders_24h": 4,
        "avg_sender_account_age_days": 365,
        "all_senders_first_time": True,
        "recipient_account_age_days": 3,
        "flagged": False,
    },
    "NEW-RECIPIENT-ATO-456": {
        "account_id": "NEW-RECIPIENT-ATO-456",
        "account_name": "Quick Cash Ltd",
        "incoming_transfers_24h": 1,
        "unique_senders_24h": 1,
        "avg_sender_account_age_days": 200,
        "all_senders_first_time": True,
        "recipient_account_age_days": 30,
        "flagged": False,
    },
    "EXTERNAL-MULE-OUT-111": {
        "account_id": "EXTERNAL-MULE-OUT-111",
        "account_name": "Offshore Holdings",
        "incoming_transfers_24h": 2,
        "unique_senders_24h": 2,
        "avg_sender_account_age_days": 10,
        "all_senders_first_time": True,
        "recipient_account_age_days": 7,
        "flagged": False,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DEMO SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_SCENARIOS = {
    # ── Normal: Mertali pays his utilities, fast and clean ──
    "normal": {
        "description": "Normal transaction - Mertali pays $85 to utilities, fast typing, no anomalies",
        "transaction": {
            "user_id": "mertali-tercan",
            "amount": 85.00,
            "currency": "CAD",
            "recipient_account_id": "landlord-utilities",
            "recipient_name": "Toronto Utilities Corp",
            "recipient_institution": "TD Bank",
            "transaction_type": "e_transfer",
            "ip_address": "24.114.52.100",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "iPhone-16-Pro-MT001",
                "os": "iOS 18.1",
                "os_version": "18.1",
                "app_version": "5.3.0",
                "screen_resolution": "1206x2622",
                "timezone": "America/Toronto",
                "language": "tr-TR",
                "is_emulator": False,
                "is_rooted_jailbroken": False,
                "is_vpn_active": False,
                "is_proxy_detected": False,
                "is_remote_desktop_active": False,
                "is_screen_sharing": False,
                "battery_level": 0.82,
                "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False,
                "phone_call_duration_ms": 0,
                "clipboard_used": False,
                "clipboard_content_type": "unknown",
                "notification_count_during_session": 3,
                "screen_brightness": 0.70,
            },
            "auth_method": "biometric",
            "timestamp": "2026-03-14T15:20:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "8", "timestamp_ms": 1000, "dwell_time_ms": 38, "flight_time_ms": 52},
                    {"key": "5", "timestamp_ms": 1052, "dwell_time_ms": 35, "flight_time_ms": 48},
                ],
                "typing_speed_wpm": 76.2,
                "error_rate": 0.01,
                "typing_rhythm_signature": [52, 48, 55, 44, 50, 43, 56, 46, 49, 51],
                "segmented_typing_detected": False,
                "paste_detected": False,
                "paste_field": "",
                "touch_events": [],
                "avg_touch_pressure": 0.47,
                "avg_touch_radius": 11.3,
                "swipe_velocity_avg": 580.0,
                "tap_duration_avg_ms": 55.0,
                "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 1200},
                    {"screen_name": "send_money", "timestamp_ms": 1200, "duration_ms": 8000},
                    {"screen_name": "confirm", "timestamp_ms": 9200, "duration_ms": 800},
                ],
                "navigation_directness_score": 0.82,
                "time_per_screen_ms": {"home": 1200, "send_money": 8000, "confirm": 800},
                "screen_familiarity_score": 0.90,
                "app_switches": [],
                "dead_time_periods": [],
                "total_dead_time_ms": 0,
                "confirm_button_hesitation_ms": 120,
                "confirm_attempts": 1,
            },
        },
    },

    # ── APP fraud: Ediz is coerced on the phone at 2am ──
    "app_fraud": {
        "description": "APP fraud under coercion - Ediz sends $2,500 to mule account at 2am while on phone",
        "transaction": {
            "user_id": "ediz-uysal",
            "amount": 2500.00,
            "currency": "CAD",
            "recipient_account_id": "NEW-MULE-ACCOUNT-789",
            "recipient_name": "John Smith",
            "recipient_institution": "Unknown Bank",
            "transaction_type": "e_transfer",
            "ip_address": "72.38.44.55",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "Galaxy-S24-EU002",
                "os": "Android 15",
                "os_version": "15",
                "app_version": "5.3.0",
                "screen_resolution": "1080x2340",
                "timezone": "America/Toronto",
                "language": "en-CA",
                "is_emulator": False,
                "is_rooted_jailbroken": False,
                "is_vpn_active": False,
                "is_proxy_detected": False,
                "is_remote_desktop_active": False,
                "is_screen_sharing": False,
                "battery_level": 0.28,
                "is_charging": True,
            },
            "session_context": {
                "is_phone_call_active": True,
                "phone_call_duration_ms": 420000,
                "clipboard_used": True,
                "clipboard_content_type": "account_number",
                "notification_count_during_session": 0,
                "screen_brightness": 0.25,
            },
            "auth_method": "password",
            "timestamp": "2026-03-14T02:34:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "2", "timestamp_ms": 1000, "dwell_time_ms": 150, "flight_time_ms": 3200},
                    {"key": "5", "timestamp_ms": 4200, "dwell_time_ms": 140, "flight_time_ms": 3500},
                    {"key": "0", "timestamp_ms": 7700, "dwell_time_ms": 160, "flight_time_ms": 4100},
                    {"key": "0", "timestamp_ms": 11800, "dwell_time_ms": 145, "flight_time_ms": 3800},
                ],
                "typing_speed_wpm": 11.5,
                "error_rate": 0.15,
                "typing_rhythm_signature": [3200, 3500, 4100, 3800, 3300, 3600, 3900, 4200, 3100, 3700],
                "segmented_typing_detected": True,
                "paste_detected": True,
                "paste_field": "recipient_account",
                "touch_events": [],
                "avg_touch_pressure": 0.35,
                "avg_touch_radius": 13.8,
                "swipe_velocity_avg": 260.0,
                "tap_duration_avg_ms": 140.0,
                "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 1500},
                    {"screen_name": "send_money", "timestamp_ms": 1500, "duration_ms": 48000},
                    {"screen_name": "confirm", "timestamp_ms": 49500, "duration_ms": 14000},
                ],
                "navigation_directness_score": 0.93,
                "time_per_screen_ms": {"home": 1500, "send_money": 48000, "confirm": 14000},
                "screen_familiarity_score": 0.18,
                "app_switches": [
                    {"timestamp_ms": 30000, "duration_away_ms": 12000},
                ],
                "dead_time_periods": [
                    {"start_ms": 15000, "end_ms": 23000, "duration_ms": 8000},
                    {"start_ms": 48000, "end_ms": 55000, "duration_ms": 7000},
                ],
                "total_dead_time_ms": 15000,
                "confirm_button_hesitation_ms": 4500,
                "confirm_attempts": 3,
            },
        },
    },

    # ── Account takeover: Someone stole Deniz's iPad ──
    "account_takeover": {
        "description": "Account takeover - Someone uses Deniz's stolen iPad, types fast (unlike Deniz), no paste",
        "transaction": {
            "user_id": "deniz-coban",
            "amount": 1200.00,
            "currency": "CAD",
            "recipient_account_id": "NEW-RECIPIENT-ATO-456",
            "recipient_name": "Quick Cash Ltd",
            "recipient_institution": "External Bank",
            "transaction_type": "e_transfer",
            "ip_address": "185.220.101.44",
            "ip_geolocation": {"lat": 52.52, "lng": 13.40, "city": "Berlin", "country": "DE"},
            "device_fingerprint": {
                "device_id": "iPad-Air-DC003",
                "os": "iPadOS 17.4",
                "os_version": "17.4",
                "app_version": "5.3.0",
                "screen_resolution": "2360x1640",
                "timezone": "Europe/Berlin",
                "language": "en-US",
                "is_emulator": False,
                "is_rooted_jailbroken": False,
                "is_vpn_active": True,
                "is_proxy_detected": False,
                "is_remote_desktop_active": False,
                "is_screen_sharing": False,
                "battery_level": 0.91,
                "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False,
                "phone_call_duration_ms": 0,
                "clipboard_used": False,
                "clipboard_content_type": "unknown",
                "notification_count_during_session": 0,
                "screen_brightness": 0.90,
            },
            "auth_method": "password",
            "timestamp": "2026-03-14T03:15:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "1", "timestamp_ms": 1000, "dwell_time_ms": 45, "flight_time_ms": 55},
                    {"key": "2", "timestamp_ms": 1055, "dwell_time_ms": 40, "flight_time_ms": 50},
                    {"key": "0", "timestamp_ms": 1105, "dwell_time_ms": 42, "flight_time_ms": 52},
                    {"key": "0", "timestamp_ms": 1157, "dwell_time_ms": 38, "flight_time_ms": 48},
                ],
                "typing_speed_wpm": 68.0,
                "error_rate": 0.01,
                "typing_rhythm_signature": [55, 50, 52, 48, 54, 46, 58, 44, 51, 49],
                "segmented_typing_detected": False,
                "paste_detected": False,
                "paste_field": "",
                "touch_events": [],
                "avg_touch_pressure": 0.38,
                "avg_touch_radius": 11.0,
                "swipe_velocity_avg": 650.0,
                "tap_duration_avg_ms": 48.0,
                "hand_dominance": "left",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 2000},
                    {"screen_name": "accounts", "timestamp_ms": 2000, "duration_ms": 3000},
                    {"screen_name": "send_money", "timestamp_ms": 5000, "duration_ms": 12000},
                    {"screen_name": "confirm", "timestamp_ms": 17000, "duration_ms": 800},
                ],
                "navigation_directness_score": 0.70,
                "time_per_screen_ms": {"home": 2000, "accounts": 3000, "send_money": 12000, "confirm": 800},
                "screen_familiarity_score": 0.60,
                "app_switches": [],
                "dead_time_periods": [],
                "total_dead_time_ms": 0,
                "confirm_button_hesitation_ms": 80,
                "confirm_attempts": 1,
            },
        },
    },

    # ── Mule network: Mertali's account is being used as a mule ──
    "mule_network": {
        "description": "Money mule - Mertali's account rapidly moves funds to offshore account",
        "transaction": {
            "user_id": "mertali-tercan",
            "amount": 1400.00,
            "currency": "CAD",
            "recipient_account_id": "EXTERNAL-MULE-OUT-111",
            "recipient_name": "Offshore Holdings",
            "recipient_institution": "Foreign Bank",
            "transaction_type": "wire",
            "ip_address": "91.132.147.88",
            "ip_geolocation": {"lat": 41.01, "lng": 28.97, "city": "Istanbul", "country": "TR"},
            "device_fingerprint": {
                "device_id": "Unknown-Android-X99",
                "os": "Android 13",
                "os_version": "13",
                "app_version": "5.3.0",
                "screen_resolution": "1080x2400",
                "timezone": "Europe/Istanbul",
                "language": "tr-TR",
                "is_emulator": True,
                "is_rooted_jailbroken": True,
                "is_vpn_active": True,
                "is_proxy_detected": False,
                "is_remote_desktop_active": False,
                "is_screen_sharing": False,
                "battery_level": 1.0,
                "is_charging": True,
            },
            "session_context": {
                "is_phone_call_active": False,
                "phone_call_duration_ms": 0,
                "clipboard_used": True,
                "clipboard_content_type": "account_number",
                "notification_count_during_session": 0,
                "screen_brightness": 0.50,
            },
            "auth_method": "password",
            "timestamp": "2026-03-14T04:30:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "1", "timestamp_ms": 1000, "dwell_time_ms": 30, "flight_time_ms": 40},
                    {"key": "4", "timestamp_ms": 1040, "dwell_time_ms": 28, "flight_time_ms": 38},
                    {"key": "0", "timestamp_ms": 1078, "dwell_time_ms": 32, "flight_time_ms": 42},
                    {"key": "0", "timestamp_ms": 1120, "dwell_time_ms": 25, "flight_time_ms": 35},
                ],
                "typing_speed_wpm": 92.0,
                "error_rate": 0.0,
                "typing_rhythm_signature": [40, 38, 42, 35, 40, 37, 43, 34, 41, 36],
                "segmented_typing_detected": False,
                "paste_detected": True,
                "paste_field": "recipient_account",
                "touch_events": [],
                "avg_touch_pressure": 0.30,
                "avg_touch_radius": 10.0,
                "swipe_velocity_avg": 800.0,
                "tap_duration_avg_ms": 35.0,
                "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 500},
                    {"screen_name": "send_money", "timestamp_ms": 500, "duration_ms": 5000},
                    {"screen_name": "confirm", "timestamp_ms": 5500, "duration_ms": 300},
                ],
                "navigation_directness_score": 0.98,
                "time_per_screen_ms": {"home": 500, "send_money": 5000, "confirm": 300},
                "screen_familiarity_score": 0.98,
                "app_switches": [],
                "dead_time_periods": [],
                "total_dead_time_ms": 0,
                "confirm_button_hesitation_ms": 30,
                "confirm_attempts": 1,
            },
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_scenario(scenario_name: str) -> dict:
    """Get a demo scenario by name."""
    return DEMO_SCENARIOS.get(scenario_name, DEMO_SCENARIOS["normal"])


def get_user_baseline(user_id: str) -> dict:
    """Get user baseline data."""
    return USER_BASELINES.get(user_id, list(USER_BASELINES.values())[0])


def get_recipient_graph(recipient_account_id: str) -> dict:
    """Get recipient graph data."""
    return RECIPIENT_GRAPH_DATA.get(recipient_account_id, {
        "account_id": recipient_account_id,
        "account_name": "Unknown",
        "incoming_transfers_24h": 0,
        "unique_senders_24h": 0,
        "avg_sender_account_age_days": 500,
        "all_senders_first_time": False,
        "recipient_account_age_days": 365,
        "flagged": False,
    })


def get_sender_profile(user_id: str) -> dict:
    """Get sender business/personal profile."""
    return SENDER_PROFILES.get(user_id, {
        "account_type": "personal",
        "occupation": "Unknown",
        "employer": "Unknown",
        "industry": "unknown",
        "account_age_days": 365,
        "typical_location": {"city": "Toronto", "country": "CA", "lat": 43.65, "lng": -79.38},
        "monthly_income_range": "0-0",
    })


def get_recipient_business_profile(recipient_account_id: str) -> dict:
    """Get recipient business profile for contextual analysis."""
    return RECIPIENT_PROFILES_BUSINESS.get(recipient_account_id, {
        "business_name": "Unknown",
        "business_type": "unknown",
        "industry": "unknown",
        "mcc_code": None,
        "mcc_description": "Unknown merchant category",
        "registered_address": None,
        "years_in_business": 0,
        "website": None,
    })
