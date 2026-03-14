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
    "friend-alex-890": {
        "business_name": "Alex Nguyen",
        "business_type": "personal",
        "industry": "personal",
        "mcc_code": None,
        "mcc_description": "Personal transfer",
        "registered_address": "Toronto, ON",
        "years_in_business": 0,
        "website": None,
    },
    "contractor-mike-456": {
        "business_name": "Mike's Renovations",
        "business_type": "sole_proprietor",
        "industry": "construction",
        "mcc_code": "1520",
        "mcc_description": "General Contractors - Residential",
        "registered_address": "88 Dundas St E, Toronto, ON",
        "years_in_business": 3,
        "website": None,
    },
    "SUSPECT-BERLIN-222": {
        "business_name": "EuroTransfer GmbH",
        "business_type": "money_service_business",
        "industry": "financial_services",
        "mcc_code": "6051",
        "mcc_description": "Non-Financial Institutions - Foreign Currency, Money Orders",
        "registered_address": None,
        "years_in_business": 0,
        "website": None,
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
    "friend-alex-890": {
        "account_id": "friend-alex-890",
        "account_name": "Alex Nguyen",
        "incoming_transfers_24h": 0,
        "unique_senders_24h": 0,
        "avg_sender_account_age_days": 600,
        "all_senders_first_time": False,
        "recipient_account_age_days": 540,
        "flagged": False,
    },
    "contractor-mike-456": {
        "account_id": "contractor-mike-456",
        "account_name": "Mike's Renovations",
        "incoming_transfers_24h": 1,
        "unique_senders_24h": 1,
        "avg_sender_account_age_days": 700,
        "all_senders_first_time": True,
        "recipient_account_age_days": 280,
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
    "SUSPECT-BERLIN-222": {
        "account_id": "SUSPECT-BERLIN-222",
        "account_name": "EuroTransfer GmbH",
        "incoming_transfers_24h": 3,
        "unique_senders_24h": 3,
        "avg_sender_account_age_days": 200,
        "all_senders_first_time": True,
        "recipient_account_age_days": 14,
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
        "transaction_direction": "incoming",
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
    # Own device, own IP, own typing rhythm (slightly stressed) → Device LOW, Behavioral LOW-MEDIUM
    # BUT: phone call active, dead time, hesitation, clipboard paste → Cognitive HIGH
    # Large amount to new recipient → Transaction HIGH, Graph MEDIUM
    "app_fraud": {
        "description": "APP fraud under coercion - Ediz sends $2,500 to mule account at 2am while on phone",
        "transaction_direction": "incoming",
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
                    {"key": "2", "timestamp_ms": 1000, "dwell_time_ms": 105, "flight_time_ms": 130},
                    {"key": "5", "timestamp_ms": 1130, "dwell_time_ms": 98, "flight_time_ms": 125},
                    {"key": "0", "timestamp_ms": 1255, "dwell_time_ms": 110, "flight_time_ms": 140},
                    {"key": "0", "timestamp_ms": 1395, "dwell_time_ms": 100, "flight_time_ms": 120},
                ],
                "typing_speed_wpm": 36.0,
                "error_rate": 0.07,
                "typing_rhythm_signature": [130, 125, 140, 120, 135, 128, 138, 115, 132, 122],
                "segmented_typing_detected": False,
                "paste_detected": True,
                "paste_field": "recipient_account",
                "touch_events": [],
                "avg_touch_pressure": 0.48,
                "avg_touch_radius": 13.2,
                "swipe_velocity_avg": 350.0,
                "tap_duration_avg_ms": 100.0,
                "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 2000},
                    {"screen_name": "send_money", "timestamp_ms": 2000, "duration_ms": 35000},
                    {"screen_name": "confirm", "timestamp_ms": 37000, "duration_ms": 8000},
                ],
                "navigation_directness_score": 0.88,
                "time_per_screen_ms": {"home": 2000, "send_money": 35000, "confirm": 8000},
                "screen_familiarity_score": 0.30,
                "app_switches": [
                    {"timestamp_ms": 20000, "duration_away_ms": 8000},
                ],
                "dead_time_periods": [
                    {"start_ms": 12000, "end_ms": 18000, "duration_ms": 6000},
                    {"start_ms": 32000, "end_ms": 37000, "duration_ms": 5000},
                ],
                "total_dead_time_ms": 11000,
                "confirm_button_hesitation_ms": 4500,
                "confirm_attempts": 3,
            },
        },
    },

    # ── Account takeover: Someone stole Deniz's iPad ──
    "account_takeover": {
        "description": "Account takeover - Someone uses Deniz's stolen iPad, types fast (unlike Deniz), no paste",
        "transaction_direction": "incoming",
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

    # ── Safe: Mertali pays groceries, fast and clean ──
    "safe_mertali": {
        "description": "Safe incoming - Mertali receives $320 payroll deposit, normal behavior",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "mertali-tercan",
            "amount": 320.00,
            "currency": "CAD",
            "recipient_account_id": "grocery-store",
            "recipient_name": "Loblaws",
            "recipient_institution": "TD Bank",
            "transaction_type": "e_transfer",
            "ip_address": "24.114.52.100",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "iPhone-16-Pro-MT001",
                "os": "iOS 18.1", "os_version": "18.1", "app_version": "5.3.0",
                "screen_resolution": "1206x2622", "timezone": "America/Toronto",
                "language": "tr-TR", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": False, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.75, "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": False, "clipboard_content_type": "unknown",
                "notification_count_during_session": 5, "screen_brightness": 0.65,
            },
            "auth_method": "biometric",
            "timestamp": "2026-03-14T10:15:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "3", "timestamp_ms": 1000, "dwell_time_ms": 40, "flight_time_ms": 50},
                    {"key": "2", "timestamp_ms": 1050, "dwell_time_ms": 36, "flight_time_ms": 46},
                    {"key": "0", "timestamp_ms": 1096, "dwell_time_ms": 38, "flight_time_ms": 52},
                ],
                "typing_speed_wpm": 79.1, "error_rate": 0.01,
                "typing_rhythm_signature": [50, 46, 52, 44, 48, 42, 55, 43, 49, 51],
                "segmented_typing_detected": False, "paste_detected": False, "paste_field": "",
                "touch_events": [], "avg_touch_pressure": 0.49, "avg_touch_radius": 11.2,
                "swipe_velocity_avg": 590.0, "tap_duration_avg_ms": 52.0, "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 1000},
                    {"screen_name": "send_money", "timestamp_ms": 1000, "duration_ms": 7000},
                    {"screen_name": "confirm", "timestamp_ms": 8000, "duration_ms": 600},
                ],
                "navigation_directness_score": 0.85, "time_per_screen_ms": {"home": 1000, "send_money": 7000, "confirm": 600},
                "screen_familiarity_score": 0.92, "app_switches": [], "dead_time_periods": [],
                "total_dead_time_ms": 0, "confirm_button_hesitation_ms": 100, "confirm_attempts": 1,
            },
        },
    },

    # ── Safe: Ediz pays pharmacy, normal speed ──
    "safe_ediz": {
        "description": "Safe outgoing - Ediz sends $145 to pharmacy, typical behavior",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "ediz-uysal",
            "amount": 145.00,
            "currency": "CAD",
            "recipient_account_id": "pharmacy",
            "recipient_name": "Shoppers Drug Mart",
            "recipient_institution": "TD Bank",
            "transaction_type": "e_transfer",
            "ip_address": "72.38.44.55",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "Galaxy-S24-EU002",
                "os": "Android 15", "os_version": "15", "app_version": "5.3.0",
                "screen_resolution": "1080x2340", "timezone": "America/Toronto",
                "language": "en-CA", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": False, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.60, "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": False, "clipboard_content_type": "unknown",
                "notification_count_during_session": 2, "screen_brightness": 0.55,
            },
            "auth_method": "biometric",
            "timestamp": "2026-03-14T12:30:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "1", "timestamp_ms": 1000, "dwell_time_ms": 95, "flight_time_ms": 110},
                    {"key": "4", "timestamp_ms": 1110, "dwell_time_ms": 88, "flight_time_ms": 105},
                    {"key": "5", "timestamp_ms": 1215, "dwell_time_ms": 92, "flight_time_ms": 100},
                ],
                "typing_speed_wpm": 43.5, "error_rate": 0.04,
                "typing_rhythm_signature": [110, 105, 100, 108, 95, 102, 112, 98, 90, 107],
                "segmented_typing_detected": False, "paste_detected": False, "paste_field": "",
                "touch_events": [], "avg_touch_pressure": 0.51, "avg_touch_radius": 13.2,
                "swipe_velocity_avg": 420.0, "tap_duration_avg_ms": 85.0, "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 3000},
                    {"screen_name": "send_money", "timestamp_ms": 3000, "duration_ms": 15000},
                    {"screen_name": "confirm", "timestamp_ms": 18000, "duration_ms": 2000},
                ],
                "navigation_directness_score": 0.45, "time_per_screen_ms": {"home": 3000, "send_money": 15000, "confirm": 2000},
                "screen_familiarity_score": 0.65, "app_switches": [], "dead_time_periods": [],
                "total_dead_time_ms": 0, "confirm_button_hesitation_ms": 800, "confirm_attempts": 1,
            },
        },
    },

    # ── Safe: Deniz pays utilities, slow and careful ──
    "safe_deniz": {
        "description": "Safe incoming - Deniz receives $75 pension deposit, slow typing, normal for her",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "deniz-coban",
            "amount": 75.00,
            "currency": "CAD",
            "recipient_account_id": "landlord-utilities",
            "recipient_name": "Toronto Utilities Corp",
            "recipient_institution": "TD Bank",
            "transaction_type": "e_transfer",
            "ip_address": "99.225.88.12",
            "ip_geolocation": {"lat": 43.70, "lng": -79.42, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "iPad-Air-DC003",
                "os": "iPadOS 17.4", "os_version": "17.4", "app_version": "5.3.0",
                "screen_resolution": "2360x1640", "timezone": "America/Toronto",
                "language": "en-CA", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": False, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.55, "is_charging": True,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": True, "clipboard_content_type": "text",
                "notification_count_during_session": 1, "screen_brightness": 0.80,
            },
            "auth_method": "password",
            "timestamp": "2026-03-14T10:45:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "7", "timestamp_ms": 1000, "dwell_time_ms": 180, "flight_time_ms": 290},
                    {"key": "5", "timestamp_ms": 1290, "dwell_time_ms": 195, "flight_time_ms": 310},
                ],
                "typing_speed_wpm": 17.8, "error_rate": 0.10,
                "typing_rhythm_signature": [290, 310, 280, 305, 325, 270, 315, 295, 300, 285],
                "segmented_typing_detected": False, "paste_detected": True, "paste_field": "amount",
                "touch_events": [], "avg_touch_pressure": 0.63, "avg_touch_radius": 16.8,
                "swipe_velocity_avg": 220.0, "tap_duration_avg_ms": 160.0, "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 8000},
                    {"screen_name": "accounts", "timestamp_ms": 8000, "duration_ms": 12000},
                    {"screen_name": "send_money", "timestamp_ms": 20000, "duration_ms": 35000},
                    {"screen_name": "confirm", "timestamp_ms": 55000, "duration_ms": 5000},
                ],
                "navigation_directness_score": 0.22, "time_per_screen_ms": {"home": 8000, "accounts": 12000, "send_money": 35000, "confirm": 5000},
                "screen_familiarity_score": 0.30, "app_switches": [], "dead_time_periods": [
                    {"start_ms": 25000, "end_ms": 32000, "duration_ms": 7000},
                ],
                "total_dead_time_ms": 7000, "confirm_button_hesitation_ms": 3200, "confirm_attempts": 2,
            },
        },
    },

    # ── Suspicious (MEDIUM): Mertali sends to a contractor he's never paid before ──
    # Everything normal EXCEPT: first-time recipient, amount above his avg ($450 vs $185 avg)
    # Behavioral LOW, Cognitive LOW, Device LOW, Transaction LOW-MED, Graph LOW
    "suspicious_mertali": {
        "description": "Medium risk - Mertali pays contractor for first time, higher than usual amount",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "mertali-tercan",
            "amount": 450.00,
            "currency": "CAD",
            "recipient_account_id": "contractor-mike-456",
            "recipient_name": "Mike's Renovations",
            "recipient_institution": "Scotiabank",
            "transaction_type": "e_transfer",
            "ip_address": "24.114.52.88",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "iPhone-16-Pro-MT001",
                "os": "iOS 18.1", "os_version": "18.1", "app_version": "5.3.0",
                "screen_resolution": "1206x2622", "timezone": "America/Toronto",
                "language": "tr-TR", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": False, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.65, "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": False, "clipboard_content_type": "unknown",
                "notification_count_during_session": 3, "screen_brightness": 0.60,
            },
            "auth_method": "biometric",
            "timestamp": "2026-03-14T15:30:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "4", "timestamp_ms": 1000, "dwell_time_ms": 40, "flight_time_ms": 54},
                    {"key": "5", "timestamp_ms": 1054, "dwell_time_ms": 37, "flight_time_ms": 50},
                    {"key": "0", "timestamp_ms": 1104, "dwell_time_ms": 39, "flight_time_ms": 52},
                ],
                "typing_speed_wpm": 75.0, "error_rate": 0.02,
                "typing_rhythm_signature": [54, 50, 52, 46, 51, 44, 57, 45, 48, 53],
                "segmented_typing_detected": False, "paste_detected": False, "paste_field": "",
                "touch_events": [], "avg_touch_pressure": 0.47, "avg_touch_radius": 11.4,
                "swipe_velocity_avg": 575.0, "tap_duration_avg_ms": 56.0, "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 1500},
                    {"screen_name": "send_money", "timestamp_ms": 1500, "duration_ms": 10000},
                    {"screen_name": "confirm", "timestamp_ms": 11500, "duration_ms": 900},
                ],
                "navigation_directness_score": 0.80, "time_per_screen_ms": {"home": 1500, "send_money": 10000, "confirm": 900},
                "screen_familiarity_score": 0.85, "app_switches": [], "dead_time_periods": [],
                "total_dead_time_ms": 0, "confirm_button_hesitation_ms": 250, "confirm_attempts": 1,
            },
        },
    },

    # ── Suspicious (MEDIUM): Ediz sends to a friend, slight hesitation ──
    # Own device, own IP, typing close to baseline
    # BUT: first-time recipient, clipboard paste, slight hesitation, evening hour
    # Behavioral LOW, Cognitive LOW-MED, Device LOW, Transaction LOW-MED, Graph LOW
    "suspicious_ediz": {
        "description": "Medium risk - Ediz sends to new friend, pastes account number, slight hesitation",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "ediz-uysal",
            "amount": 350.00,
            "currency": "CAD",
            "recipient_account_id": "friend-alex-890",
            "recipient_name": "Alex Nguyen",
            "recipient_institution": "RBC",
            "transaction_type": "e_transfer",
            "ip_address": "72.38.44.55",
            "ip_geolocation": {"lat": 43.65, "lng": -79.38, "city": "Toronto", "country": "CA"},
            "device_fingerprint": {
                "device_id": "Galaxy-S24-EU002",
                "os": "Android 15", "os_version": "15", "app_version": "5.3.0",
                "screen_resolution": "1080x2340", "timezone": "America/Toronto",
                "language": "en-CA", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": False, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.55, "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": True, "clipboard_content_type": "account_number",
                "notification_count_during_session": 1, "screen_brightness": 0.45,
            },
            "auth_method": "biometric",
            "timestamp": "2026-03-14T19:15:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "3", "timestamp_ms": 1000, "dwell_time_ms": 100, "flight_time_ms": 112},
                    {"key": "5", "timestamp_ms": 1112, "dwell_time_ms": 90, "flight_time_ms": 105},
                    {"key": "0", "timestamp_ms": 1217, "dwell_time_ms": 94, "flight_time_ms": 100},
                ],
                "typing_speed_wpm": 41.0, "error_rate": 0.05,
                "typing_rhythm_signature": [112, 105, 100, 108, 95, 102, 110, 98, 90, 107],
                "segmented_typing_detected": False, "paste_detected": True, "paste_field": "recipient_account",
                "touch_events": [], "avg_touch_pressure": 0.50, "avg_touch_radius": 13.1,
                "swipe_velocity_avg": 410.0, "tap_duration_avg_ms": 86.0, "hand_dominance": "right",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 3000},
                    {"screen_name": "send_money", "timestamp_ms": 3000, "duration_ms": 18000},
                    {"screen_name": "confirm", "timestamp_ms": 21000, "duration_ms": 2500},
                ],
                "navigation_directness_score": 0.43, "time_per_screen_ms": {"home": 3000, "send_money": 18000, "confirm": 2500},
                "screen_familiarity_score": 0.50, "app_switches": [],
                "dead_time_periods": [],
                "total_dead_time_ms": 0, "confirm_button_hesitation_ms": 1500, "confirm_attempts": 1,
            },
        },
    },

    # ── Suspicious (HIGH): Deniz account takeover ──
    # Different typing (fast vs baseline slow), VPN from Berlin, different hand
    # BUT: known device (stolen iPad), no phone call, no clipboard
    # Expected: Behavioral HIGH, Cognitive LOW, Device HIGH, Transaction MEDIUM, Graph MEDIUM
    "suspicious_deniz": {
        "description": "High risk - Someone uses Deniz's stolen iPad from Berlin, fast typing mismatch, VPN active",
        "transaction_direction": "incoming",
        "transaction": {
            "user_id": "deniz-coban",
            "amount": 760.00,
            "currency": "CAD",
            "recipient_account_id": "SUSPECT-BERLIN-222",
            "recipient_name": "EuroTransfer GmbH",
            "recipient_institution": "External Bank",
            "transaction_type": "e_transfer",
            "ip_address": "185.220.101.44",
            "ip_geolocation": {"lat": 52.52, "lng": 13.40, "city": "Berlin", "country": "DE"},
            "device_fingerprint": {
                "device_id": "iPad-Air-DC003",
                "os": "iPadOS 17.4", "os_version": "17.4", "app_version": "5.3.0",
                "screen_resolution": "2360x1640", "timezone": "Europe/Berlin",
                "language": "en-US", "is_emulator": False, "is_rooted_jailbroken": False,
                "is_vpn_active": True, "is_proxy_detected": False,
                "is_remote_desktop_active": False, "is_screen_sharing": False,
                "battery_level": 0.88, "is_charging": False,
            },
            "session_context": {
                "is_phone_call_active": False, "phone_call_duration_ms": 0,
                "clipboard_used": False, "clipboard_content_type": "unknown",
                "notification_count_during_session": 0, "screen_brightness": 0.85,
            },
            "auth_method": "password",
            "timestamp": "2026-03-14T04:00:00Z",
            "behavioral_telemetry": {
                "keystroke_events": [
                    {"key": "8", "timestamp_ms": 1000, "dwell_time_ms": 42, "flight_time_ms": 55},
                    {"key": "8", "timestamp_ms": 1055, "dwell_time_ms": 38, "flight_time_ms": 50},
                    {"key": "0", "timestamp_ms": 1105, "dwell_time_ms": 40, "flight_time_ms": 48},
                ],
                "typing_speed_wpm": 72.0, "error_rate": 0.02,
                "typing_rhythm_signature": [55, 50, 48, 52, 54, 47, 56, 45, 53, 49],
                "segmented_typing_detected": False, "paste_detected": False, "paste_field": "",
                "touch_events": [], "avg_touch_pressure": 0.40, "avg_touch_radius": 11.5,
                "swipe_velocity_avg": 620.0, "tap_duration_avg_ms": 50.0, "hand_dominance": "left",
                "navigation_path": [
                    {"screen_name": "home", "timestamp_ms": 0, "duration_ms": 1500},
                    {"screen_name": "send_money", "timestamp_ms": 1500, "duration_ms": 10000},
                    {"screen_name": "confirm", "timestamp_ms": 11500, "duration_ms": 600},
                ],
                "navigation_directness_score": 0.72, "time_per_screen_ms": {"home": 1500, "send_money": 10000, "confirm": 600},
                "screen_familiarity_score": 0.55, "app_switches": [], "dead_time_periods": [],
                "total_dead_time_ms": 0, "confirm_button_hesitation_ms": 100, "confirm_attempts": 1,
            },
        },
    },

    # ── Mule network: Mertali's account is being used as a mule ──
    # Unknown device, emulator, foreign IP → Device HIGH, Behavioral HIGH
    # Offshore recipient, wire transfer → Transaction HIGH, Graph HIGH
    # No phone call, no dead time, no hesitation (automated) → Cognitive LOW
    "mule_network": {
        "description": "Money mule - Mertali's account rapidly moves funds to offshore account via automated setup",
        "transaction_direction": "incoming",
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
                "clipboard_used": False,
                "clipboard_content_type": "unknown",
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
                "paste_detected": False,
                "paste_field": "",
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
