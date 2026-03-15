import React, { useState, useRef, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  SafeAreaView,
  Platform,
  Animated,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { TelemetryTracker } from "../lib/telemetry";
import { generateScenario } from "../lib/api";
import SendMoneyModal from "../components/SendMoneyModal";

interface Props {
  user: { userId: string; name: string };
  tracker: TelemetryTracker | null;
  onLogout: () => void;
}

export default function HomeScreen({ user, tracker, onLogout }: Props) {
  const [balance, setBalance] = useState(
    () => Math.floor(Math.random() * 1000 + 1000) + Math.random() * 0.99
  );
  const [showSendMoney, setShowSendMoney] = useState(false);
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [demoExpanded, setDemoExpanded] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const toastOpacity = useRef(new Animated.Value(0)).current;

  const showToast = useCallback(
    (message: string) => {
      setToast(message);
      Animated.sequence([
        Animated.timing(toastOpacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.delay(2500),
        Animated.timing(toastOpacity, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start(() => setToast(null));
    },
    [toastOpacity]
  );

  const handleInteraction = () => {
    tracker?.recordTouch(200, 400, "press");
  };

  const handleGenerate = async (type: "safe" | "suspicious") => {
    handleInteraction();
    setDemoLoading(type);

    const amount = parseFloat((Math.random() * 400 + 50).toFixed(2));
    setBalance((b) => b + amount);
    showToast(
      type === "safe"
        ? `Incoming $${amount.toFixed(2)} for ${user.name}`
        : `Incoming $${amount.toFixed(2)} for ${user.name} — analyzing...`
    );

    try {
      const result = await generateScenario(user.userId, type);
      const assessment = result?.assessment || {};
      const score =
        assessment?.meta?.cumulative_fraud_score ?? result?.cumulative_fraud_score ?? "N/A";
      const risk = assessment?.meta?.risk_level ?? result?.risk_level ?? "unknown";
      Alert.alert(
        "Pipeline Complete",
        `${user.name}\nFraud Score: ${score}/100\nRisk: ${risk}`,
        [{ text: "OK" }]
      );
    } catch {
      Alert.alert("Error", "Could not reach backend. Is it running?");
    }
    setDemoLoading(null);
  };

  const placeholderTransactions = [
    { name: "Tim Hortons", amount: -4.85, date: "Mar 12" },
    { name: "Shopify Payroll", amount: 3250.0, date: "Mar 10" },
    { name: "Netflix", amount: -16.49, date: "Mar 8" },
    { name: "Interac e-Transfer", amount: -200.0, date: "Mar 5" },
  ];

  return (
    <SafeAreaView style={styles.container} onTouchStart={handleInteraction}>
      {/* Toast Notification */}
      {toast && (
        <Animated.View style={[styles.toast, { opacity: toastOpacity }]}>
          <Ionicons name="checkmark-circle" size={16} color="#34A853" />
          <Text style={styles.toastText}>{toast}</Text>
        </Animated.View>
      )}

      {/* Collapsible Demo Seed Bar */}
      <View style={styles.demoBar}>
        <TouchableOpacity
          onPress={() => setDemoExpanded(!demoExpanded)}
          style={styles.demoChevron}
        >
          <Ionicons
            name={demoExpanded ? "chevron-down" : "chevron-forward"}
            size={14}
            color="#555"
          />
        </TouchableOpacity>
        {demoExpanded && (
          <View style={styles.demoContent}>
            <Text style={styles.demoHint}>Data seeding for demo purposes</Text>
            <View style={styles.demoRow}>
              <Text style={styles.demoLabel}>Generate (Incoming):</Text>
              <TouchableOpacity
                style={styles.demoButton}
                onPress={() => handleGenerate("safe")}
                disabled={!!demoLoading}
              >
                <Text style={styles.demoButtonText}>
                  {demoLoading === "safe" ? "..." : "Safe"}
                </Text>
              </TouchableOpacity>
              <Text style={styles.demoDash}>-</Text>
              <TouchableOpacity
                style={[styles.demoButton, styles.demoButtonDanger]}
                onPress={() => handleGenerate("suspicious")}
                disabled={!!demoLoading}
              >
                <Text style={styles.demoButtonText}>
                  {demoLoading === "suspicious" ? "..." : "Suspicious"}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>

      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.welcome}>Welcome, {user.name}!</Text>
          <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>

        {/* Account Card */}
        <View style={styles.accountCard}>
          <View style={styles.accountHeader}>
            <Ionicons name="wallet-outline" size={20} color="#34A853" />
            <Text style={styles.accountType}>Chequing Account</Text>
          </View>
          <Text style={styles.balanceLabel}>Available Balance</Text>
          <Text style={styles.balance}>${balance.toFixed(2)}</Text>
          <Text style={styles.accountNumber}>
            **** **** **** 4821
          </Text>
        </View>

        {/* Actions */}
        <View style={styles.actionsRow}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => {
              handleInteraction();
              tracker?.recordNavigation("send_money");
              setShowSendMoney(true);
            }}
          >
            <Ionicons name="send-outline" size={22} color="#34A853" />
            <Text style={styles.actionText}>Send{"\n"}Money</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => {
              handleInteraction();
              Alert.alert(
                "Coming Soon",
                "Request Money is not available in demo."
              );
            }}
          >
            <Ionicons name="download-outline" size={22} color="#34A853" />
            <Text style={styles.actionText}>Request{"\n"}Money</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => {
              handleInteraction();
              setHistoryExpanded(!historyExpanded);
            }}
          >
            <Ionicons name="time-outline" size={22} color="#34A853" />
            <Text style={styles.actionText}>Transaction{"\n"}History</Text>
          </TouchableOpacity>
        </View>

        {/* Transaction History Placeholder */}
        <View style={styles.historySection}>
          <TouchableOpacity
            style={styles.historyHeader}
            onPress={() => {
              handleInteraction();
              setHistoryExpanded(!historyExpanded);
            }}
          >
            <Text style={styles.historyTitle}>Recent Transactions</Text>
            <Ionicons
              name={historyExpanded ? "chevron-up" : "chevron-down"}
              size={18}
              color="#8E8E93"
            />
          </TouchableOpacity>

          {historyExpanded &&
            placeholderTransactions.map((tx, i) => (
              <View key={i} style={styles.txRow}>
                <View>
                  <Text style={styles.txName}>{tx.name}</Text>
                  <Text style={styles.txDate}>{tx.date}</Text>
                </View>
                <Text
                  style={[
                    styles.txAmount,
                    tx.amount > 0 ? styles.txPositive : styles.txNegative,
                  ]}
                >
                  {tx.amount > 0 ? "+" : ""}${Math.abs(tx.amount).toFixed(2)}
                </Text>
              </View>
            ))}
        </View>
      </View>

      {/* Send Money Modal */}
      <SendMoneyModal
        visible={showSendMoney}
        userId={user.userId}
        tracker={tracker}
        onClose={() => {
          tracker?.recordNavigation("home");
          setShowSendMoney(false);
        }}
        onSent={(amount, name) => {
          setBalance((b) => b - amount);
          showToast(`Money sent $${amount.toFixed(2)} to ${name}`);
        }}
        onAnalysisComplete={(score, risk, amount, name) => {
          showToast(`${name}: Score ${score}/100 (${risk})`);
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0A0A0A",
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  toast: {
    position: "absolute",
    top: 50,
    left: 24,
    right: 24,
    backgroundColor: "#1B3A28",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    zIndex: 100,
    borderWidth: 1,
    borderColor: "#34A853",
  },
  toastText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "500",
    flex: 1,
  },
  demoBar: {
    flexDirection: "row",
    alignItems: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 6,
  },
  demoChevron: {
    paddingTop: 2,
    paddingRight: 6,
  },
  demoContent: {
    flex: 1,
  },
  demoHint: {
    color: "#555",
    fontSize: 10,
    marginBottom: 3,
  },
  demoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  demoLabel: {
    color: "#8E8E93",
    fontSize: 11,
    fontWeight: "500",
  },
  demoDash: {
    color: "#555",
    fontSize: 11,
  },
  demoButton: {
    backgroundColor: "#1B3A28",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: "#34A853",
  },
  demoButtonDanger: {
    backgroundColor: "#3A1B1B",
    borderColor: "#E24B4A",
  },
  demoButtonText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "600",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 12,
    paddingBottom: 16,
  },
  welcome: {
    fontSize: 22,
    fontWeight: "700",
    color: "#FFFFFF",
  },
  logoutButton: {
    backgroundColor: "#1C1C1E",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#2C2C2E",
  },
  logoutText: {
    color: "#E24B4A",
    fontSize: 13,
    fontWeight: "600",
  },
  accountCard: {
    backgroundColor: "#1C1C1E",
    borderRadius: 14,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#2C2C2E",
  },
  accountHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 14,
  },
  accountType: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "600",
  },
  balanceLabel: {
    color: "#8E8E93",
    fontSize: 12,
    marginBottom: 4,
  },
  balance: {
    color: "#FFFFFF",
    fontSize: 32,
    fontWeight: "800",
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  accountNumber: {
    color: "#3A3A3C",
    fontSize: 13,
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
  },
  actionsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 20,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: "#1C1C1E",
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#2C2C2E",
    gap: 8,
  },
  actionText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "500",
    textAlign: "center",
    lineHeight: 16,
  },
  historySection: {
    backgroundColor: "#1C1C1E",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#2C2C2E",
    overflow: "hidden",
  },
  historyHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
  },
  historyTitle: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "600",
  },
  txRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: "#2C2C2E",
  },
  txName: {
    color: "#FFFFFF",
    fontSize: 14,
    fontWeight: "500",
  },
  txDate: {
    color: "#8E8E93",
    fontSize: 12,
    marginTop: 2,
  },
  txAmount: {
    fontSize: 15,
    fontWeight: "600",
  },
  txPositive: {
    color: "#34A853",
  },
  txNegative: {
    color: "#FFFFFF",
  },
});
