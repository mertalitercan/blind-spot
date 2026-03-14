"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";

interface Assessment {
  id: string;
  user_id: string;
  user_name: string;
  timestamp: string;
  cumulative_fraud_score: number;
  risk_level: string;
  transaction_direction: string;
  assessment: any;
}

interface Alert {
  id: string;
  user_name: string;
  score: number;
  risk_level: string;
  message: string;
  timestamp: string;
  read: boolean;
}

const TAB_STYLES: Record<string, { active: string; dot: string; label: string }> = {
  all: { active: "border-indigo-400 text-indigo-300", dot: "", label: "All Cases" },
  red: { active: "border-red-400 text-red-300", dot: "bg-red-400", label: "High Risk" },
  yellow: { active: "border-amber-400 text-amber-300", dot: "bg-amber-400", label: "Medium" },
  green: { active: "border-emerald-400 text-emerald-300", dot: "bg-emerald-400", label: "Low Risk" },
};

function scoreGradient(score: number) {
  if (score >= 71) return "from-red-500/20 to-red-500/5 border-red-500/20";
  if (score >= 31) return "from-amber-500/20 to-amber-500/5 border-amber-500/20";
  return "from-emerald-500/20 to-emerald-500/5 border-emerald-500/20";
}

function scoreText(score: number) {
  if (score >= 71) return "text-red-400";
  if (score >= 31) return "text-amber-400";
  return "text-emerald-400";
}

export default function DashboardPage() {
  const [tab, setTab] = useState<"all" | "green" | "yellow" | "red">("all");
  const [users, setUsers] = useState<Assessment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const router = useRouter();

  const fetchData = useCallback(async () => {
    try {
      const [usersRes, alertsRes] = await Promise.all([
        fetch("/api/dashboard/users"),
        fetch("/api/dashboard/alerts"),
      ]);
      setUsers(await usersRes.json());
      setAlerts(await alertsRes.json());
    } catch {
      /* backend not running */
    }
  }, []);

  useEffect(() => {
    if (sessionStorage.getItem("authed") !== "true") {
      router.push("/");
      return;
    }
    fetchData();

    const ws = new WebSocket("ws://localhost:8000/ws/notifications");
    wsRef.current = ws;
    ws.onmessage = () => fetchData();
    ws.onclose = () => setTimeout(() => fetchData(), 3000);

    return () => ws.close();
  }, [fetchData, router]);

  const filteredUsers =
    tab === "all" ? users : users.filter((u) => u.risk_level === tab);
  const unreadCount = alerts.filter((a) => !a.read).length;

  const markRead = async (id: string) => {
    await fetch(`/api/dashboard/alerts/${id}/read`, { method: "PATCH" });
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a))
    );
  };

  return (
    <div className="min-h-screen">
      {/* Top Bar */}
      <header className="border-b border-[#1E1E35] px-8 py-5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl tracking-tight">
            Blind<span className="font-bold">Spot</span>
          </h1>
          <div className="h-4 w-px bg-[#1E1E35]" />
          <span className="text-xs text-slate-500 tracking-widest uppercase">
            Monitoring
          </span>
        </div>

        <div className="flex items-center gap-5">
          {/* Live indicator */}
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </div>

          {/* Notification Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifs(!showNotifs)}
              className="relative p-2 rounded-lg hover:bg-[#0F0F1A] transition"
            >
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full text-[9px] font-bold flex items-center justify-center text-white">
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifs && (
              <div className="absolute right-0 top-12 w-[400px] bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl shadow-2xl shadow-black/50 z-50 max-h-[500px] overflow-y-auto">
                <div className="p-4 border-b border-[#1E1E35] flex justify-between items-center">
                  <span className="font-semibold text-sm">Notifications</span>
                  <span className="text-xs text-slate-500">{unreadCount} new</span>
                </div>
                {alerts.length === 0 ? (
                  <p className="p-6 text-sm text-slate-600 text-center">
                    No activity yet
                  </p>
                ) : (
                  alerts.slice(0, 20).map((alert) => (
                    <div
                      key={alert.id}
                      onClick={() => markRead(alert.id)}
                      className={`p-4 border-b border-[#1E1E35]/50 cursor-pointer hover:bg-[#141425] transition ${
                        !alert.read ? "bg-[#141425]" : ""
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                            alert.risk_level === "red"
                              ? "bg-red-400"
                              : alert.risk_level === "yellow"
                              ? "bg-amber-400"
                              : "bg-emerald-400"
                          }`}
                        />
                        <div className="min-w-0">
                          <p className="text-sm leading-relaxed">{alert.message}</p>
                          <p className="text-xs text-slate-600 mt-1">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          <button
            onClick={() => {
              sessionStorage.removeItem("authed");
              router.push("/");
            }}
            className="text-xs text-slate-500 hover:text-slate-300 transition"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="p-8">
        {/* Risk Level Tabs */}
        <div className="flex gap-1 mb-8 border-b border-[#1E1E35]">
          {(["all", "red", "yellow", "green"] as const).map((level) => {
            const info = TAB_STYLES[level];
            const count =
              level === "all"
                ? users.length
                : users.filter((u) => u.risk_level === level).length;
            return (
              <button
                key={level}
                onClick={() => setTab(level)}
                className={`px-5 py-3 text-sm font-medium border-b-2 -mb-px transition flex items-center gap-2 ${
                  tab === level
                    ? info.active
                    : "border-transparent text-slate-500 hover:text-slate-300"
                }`}
              >
                {info.dot && (
                  <div className={`w-2 h-2 rounded-full ${info.dot}`} />
                )}
                {info.label}
                <span className="text-xs opacity-60">({count})</span>
              </button>
            );
          })}
        </div>

        {/* User Cards */}
        {filteredUsers.length === 0 ? (
          <div className="text-center py-24">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-slate-700" />
              <div className="w-2 h-2 rounded-full bg-slate-700" />
              <div className="w-2 h-2 rounded-full bg-slate-700" />
            </div>
            <p className="text-slate-500 text-lg font-light">No flagged users</p>
            <p className="text-slate-600 text-sm mt-2">
              Trigger a scenario from the mobile app to see results
            </p>
          </div>
        ) : (
          <div className="grid gap-3">
            {filteredUsers.map((user) => (
              <div
                key={user.id}
                onClick={() => router.push(`/dashboard/user/${user.id}`)}
                className={`bg-gradient-to-r ${scoreGradient(
                  user.cumulative_fraud_score
                )} border rounded-2xl p-5 flex items-center justify-between cursor-pointer hover:scale-[1.005] transition-all duration-200`}
              >
                <div className="flex items-center gap-5">
                  <div className="relative">
                    <svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
                      <circle
                        cx="18"
                        cy="18"
                        r="15"
                        fill="none"
                        stroke="#1E1E35"
                        strokeWidth="3"
                      />
                      <circle
                        cx="18"
                        cy="18"
                        r="15"
                        fill="none"
                        stroke={
                          user.cumulative_fraud_score >= 71
                            ? "#f87171"
                            : user.cumulative_fraud_score >= 31
                            ? "#fbbf24"
                            : "#34d399"
                        }
                        strokeWidth="3"
                        strokeDasharray={`${
                          (user.cumulative_fraud_score / 100) * 94.2
                        } 94.2`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <span
                      className={`absolute inset-0 flex items-center justify-center text-sm font-bold ${scoreText(
                        user.cumulative_fraud_score
                      )}`}
                    >
                      {user.cumulative_fraud_score}
                    </span>
                  </div>

                  <div>
                    <p className="font-semibold text-lg">{user.user_name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {user.user_id} ·{" "}
                      {new Date(user.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-[10px] font-medium tracking-wider uppercase text-slate-500 bg-[#1E1E35] px-2.5 py-1 rounded-lg">
                    {user.transaction_direction === "incoming" ? "Incoming" : "Outgoing"}
                  </span>
                  <span
                    className={`text-xs font-medium tracking-wide uppercase ${scoreText(
                      user.cumulative_fraud_score
                    )}`}
                  >
                    {user.risk_level === "red"
                      ? "High Risk"
                      : user.risk_level === "yellow"
                      ? "Medium Risk"
                      : "Low Risk"}
                  </span>
                  <svg
                    className="w-4 h-4 text-slate-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
