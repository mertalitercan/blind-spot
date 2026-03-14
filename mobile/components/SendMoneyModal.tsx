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

interface Props {
  visible: boolean;
  userId: string;
  tracker: TelemetryTracker | null;
  onClose: () => void;
  onSent: (amount: number, recipientName: string) => void;
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

  const handleSend = async () => {
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
    onSent(parsedAmount, recipientName.trim());
    resetForm();
    onClose();
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
