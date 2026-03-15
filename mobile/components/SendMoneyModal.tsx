import React, { useState, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { TelemetryTracker } from "../lib/telemetry";
import { submitTransaction } from "../lib/api";

interface Props {
  visible: boolean;
  userId: string;
  tracker: TelemetryTracker | null;
  onClose: () => void;
  onSent: (amount: number, recipientName: string) => void;
  onAnalysisComplete?: (score: string, risk: string, amount: number, name: string) => void;
}

const NAME_TO_ID: Record<string, string> = {
  "mertali tercan": "mertali-tercan",
  "mertali": "mertali-tercan",
  "ediz uysal": "ediz-uysal",
  "ediz": "ediz-uysal",
  "deniz coban": "deniz-coban",
  "deniz": "deniz-coban",
};

export default function SendMoneyModal({
  visible,
  userId,
  tracker,
  onClose,
  onSent,
  onAnalysisComplete,
}: Props) {
  const [recipientName, setRecipientName] = useState("");
  const [amount, setAmount] = useState("");
  const prevTexts = useRef<Record<string, string>>({
    recipientName: "",
    amount: "",
  });

  const handleTextChange = (
    field: string,
    value: string,
    setter: (v: string) => void
  ) => {
    const prev = prevTexts.current[field] || "";
    tracker?.recordTextChange(field, value, prev);
    prevTexts.current[field] = value;
    setter(value);
  };

  const resolveRecipientId = (name: string): string => {
    const key = name.trim().toLowerCase();
    return NAME_TO_ID[key] || key.replace(/\s+/g, "-");
  };

  const handleSend = () => {
    if (!recipientName.trim() || !amount.trim()) {
      Alert.alert("Missing Fields", "Please fill in all fields.");
      return;
    }

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      Alert.alert("Invalid Amount", "Please enter a valid amount.");
      return;
    }

    tracker?.recordConfirmPress();

    // Capture telemetry snapshot BEFORE closing
    const snapshot = tracker?.getSnapshot();
    const recipientId = resolveRecipientId(recipientName);
    const name = recipientName.trim();

    // Immediately: update balance, show toast, close modal
    onSent(parsedAmount, name);
    resetForm();
    onClose();

    // Build payload and fire analysis in background
    const payload = {
      user_id: userId,
      amount: parsedAmount,
      currency: "CAD",
      recipient_account_id: recipientId,
      recipient_name: name,
      recipient_institution: "Interac",
      transaction_type: "e_transfer",
      ip_address: "24.114.52.100",
      ip_geolocation: { lat: 43.65, lng: -79.38, city: "Toronto", country: "CA" },
      device_fingerprint: {
        device_id: `mobile-${userId}`,
        os: Platform.OS === "ios" ? "iOS 18.1" : "Android 15",
        os_version: Platform.OS === "ios" ? "18.1" : "15",
        app_version: "5.3.0",
        screen_resolution: "1206x2622",
        timezone: "America/Toronto",
        language: "en-CA",
        is_emulator: false,
        is_rooted_jailbroken: false,
        is_vpn_active: false,
        is_proxy_detected: false,
        is_remote_desktop_active: false,
        is_screen_sharing: false,
        battery_level: 0.72,
        is_charging: false,
      },
      session_context: {
        is_phone_call_active: false,
        phone_call_duration_ms: 0,
        clipboard_used: snapshot?.paste_detected || false,
        clipboard_content_type: snapshot?.paste_detected ? "account_number" : "unknown",
        notification_count_during_session: 0,
        screen_brightness: 0.6,
      },
      auth_method: "biometric",
      timestamp: new Date().toISOString(),
      behavioral_telemetry: {
        keystroke_events: (snapshot?.keystroke_events || []).slice(0, 10).map((e) => ({
          key: "*",
          timestamp_ms: e.timestamp_ms,
          dwell_time_ms: 50,
          flight_time_ms: e.timestamp_ms > 0 ? 80 : 0,
        })),
        typing_speed_wpm: snapshot?.typing_speed_wpm || 0,
        error_rate: snapshot?.error_rate || 0,
        typing_rhythm_signature: snapshot?.typing_rhythm_signature || [],
        segmented_typing_detected: snapshot?.segmented_typing_detected || false,
        paste_detected: snapshot?.paste_detected || false,
        paste_field: snapshot?.paste_field || "",
        touch_events: [],
        avg_touch_pressure: snapshot?.avg_touch_pressure || 0.45,
        avg_touch_radius: snapshot?.avg_touch_radius || 12.0,
        swipe_velocity_avg: 450.0,
        tap_duration_avg_ms: 70.0,
        hand_dominance: snapshot?.hand_dominance || "right",
        navigation_path: (snapshot?.navigation_path || []).map((n) => ({
          screen_name: n.screen_name,
          timestamp_ms: n.timestamp_ms,
          duration_ms: n.duration_ms,
        })),
        navigation_directness_score: snapshot?.navigation_directness_score || 0.5,
        time_per_screen_ms: Object.fromEntries(
          (snapshot?.navigation_path || []).map((n) => [n.screen_name, n.duration_ms])
        ),
        screen_familiarity_score: snapshot?.screen_familiarity_score || 0.5,
        app_switches: snapshot?.app_switches || [],
        dead_time_periods: snapshot?.dead_time_periods || [],
        total_dead_time_ms: snapshot?.total_dead_time_ms || 0,
        confirm_button_hesitation_ms: snapshot?.confirm_button_hesitation_ms || 0,
        confirm_attempts: snapshot?.confirm_attempts || 1,
      },
    };

    // Fire and forget — notify via callback when done
    submitTransaction(payload)
      .then((result) => {
        const assessment = result?.assessment || {};
        const score = String(assessment?.meta?.cumulative_fraud_score ?? "N/A");
        const risk = String(assessment?.meta?.risk_level ?? "unknown");
        onAnalysisComplete?.(score, risk, parsedAmount, name);
      })
      .catch(() => {
        // Transfer already went through visually — silently ignore
      });
  };

  const resetForm = () => {
    setRecipientName("");
    setAmount("");
    prevTexts.current = { recipientName: "", amount: "" };
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose}>
            <Ionicons name="close" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.title}>Send Money</Text>
          <View style={{ width: 24 }} />
        </View>

        {/* Form */}
        <View style={styles.form}>
          <Text style={styles.label}>Recipient Name</Text>
          <TextInput
            style={styles.input}
            value={recipientName}
            onChangeText={(v) =>
              handleTextChange("recipientName", v, setRecipientName)
            }
            placeholder="e.g. Deniz Coban"
            placeholderTextColor="#555"
            autoCorrect={false}
            onFocus={() => tracker?.recordConfirmApproach()}
          />

          <Text style={styles.label}>Amount (CAD)</Text>
          <TextInput
            style={styles.input}
            value={amount}
            onChangeText={(v) => handleTextChange("amount", v, setAmount)}
            placeholder="0.00"
            placeholderTextColor="#555"
            keyboardType="decimal-pad"
          />

          <TouchableOpacity
            style={styles.sendButton}
            onPress={() => {
              tracker?.recordConfirmApproach();
              handleSend();
            }}
            activeOpacity={0.8}
          >
            <Text style={styles.sendButtonText}>Send e-Transfer</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0A0A0A",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#2C2C2E",
  },
  title: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },
  form: {
    padding: 24,
  },
  label: {
    fontSize: 13,
    fontWeight: "500",
    color: "#8E8E93",
    marginBottom: 6,
    marginLeft: 2,
  },
  input: {
    backgroundColor: "#1C1C1E",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: "#FFFFFF",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#2C2C2E",
  },
  sendButton: {
    backgroundColor: "#34A853",
    borderRadius: 10,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 12,
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },
});
