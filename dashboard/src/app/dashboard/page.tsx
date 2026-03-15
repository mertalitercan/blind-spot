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
  paused?: boolean;
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

interface ProcessingCard {
  id: string;
  user_id: string;
  user_name: string;
  agents: Record<string, { score: number; confidence: number }>;
  step: string;
}

const AGENT_ORDER = [
  { key: "behavioral", label: "Behavioral" },
  { key: "cognitive", label: "Cognitive" },
  { key: "transaction", label: "Transaction" },
  { key: "device", label: "Device" },
  { key: "graph", label: "Graph" },
  { key: "metascorer", label: "Meta-Scorer" },
];

function getStepLabel(agents: Record<string, any>): string {
  const done = Object.keys(agents);
  if (done.includes("metascorer")) return "Finalizing assessment";
  if (done.includes("graph") || done.includes("device")) {
    if (done.includes("graph") && done.includes("device")) return "Running meta-reasoning synthesis";
    return "Analyzing device & network data";
  }
  if (done.length >= 1) return "Analyzing behavior, cognition & transaction";
  return "Collecting user profile data";
}

const TAB_STYLES: Record<string, { active: string; dot: string; label: string }> = {
  all: { active: "border-[#2E7D32] text-[#2E7D32]", dot: "", label: "All Cases" },
  red: { active: "border-red-400 text-red-300", dot: "bg-red-400", label: "High Risk" },
  yellow: { active: "border-amber-400 text-amber-300", dot: "bg-amber-400", label: "Medium" },
  green: { active: "border-[#2E7D32] text-[#2E7D32]", dot: "bg-[#2E7D32]", label: "Low Risk" },
};

function scoreGradient(score: number) {
  if (score >= 71) return "from-red-500/20 to-red-500/5 border-red-500/20";
  if (score >= 31) return "from-amber-500/20 to-amber-500/5 border-amber-500/20";
  return "from-[#2E7D32]/20 to-[#2E7D32]/5 border-[#2E7D32]/20";
}

function scoreText(score: number) {
  if (score >= 71) return "text-red-400";
  if (score >= 31) return "text-amber-400";
  return "text-[#2E7D32]";
}

function CaseCard({
  user,
  isNew,
  onNavigate,
  onTogglePause,
  onDismiss,
}: {
  user: Assessment;
  isNew: boolean;
  onNavigate: () => void;
  onTogglePause: (e: React.MouseEvent) => void;
  onDismiss: (e: React.MouseEvent) => void;
}) {
  const isPaused = !!user.paused;
  return (
    <div
      onClick={onNavigate}
      className={`bg-gradient-to-r ${scoreGradient(
        user.cumulative_fraud_score
      )} border rounded-2xl p-5 flex items-center justify-between cursor-pointer hover:scale-[1.005] transition-all duration-200 ${
        isNew ? "animate-[slideDown_0.5s_ease-out]" : ""
      }`}
    >
      <div className="flex items-center gap-5">
        <div className="relative">
          <svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15" fill="none" stroke="#1E1E35" strokeWidth="3" />
            <circle
              cx="18" cy="18" r="15" fill="none"
              stroke={
                user.cumulative_fraud_score >= 71
                  ? "#f87171"
                  : user.cumulative_fraud_score >= 31
                  ? "#fbbf24"
                  : "#2E7D32"
              }
              strokeWidth="3"
              strokeDasharray={`${(user.cumulative_fraud_score / 100) * 94.2} 94.2`}
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
          {isPaused && (
            <p className="text-xs text-red-300/80 mt-0.5 line-clamp-1 max-w-md">
              Account paused — {user.assessment?.meta?.reasoning?.split(".")[0] || "Suspicious activity detected"}.
            </p>
          )}
          <p className="text-xs text-slate-500 mt-0.5">
            {user.user_id} · {new Date(user.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-[10px] font-medium tracking-wider uppercase text-slate-500 bg-[#1E1E35] px-2.5 py-1 rounded-lg">
          {user.transaction_direction === "incoming" ? "Incoming" : "Outgoing"}
        </span>
        <span className={`text-xs font-medium tracking-wide uppercase ${scoreText(user.cumulative_fraud_score)}`}>
          {user.risk_level === "red" ? "High Risk" : user.risk_level === "yellow" ? "Medium Risk" : "Low Risk"}
        </span>

        <button
          onClick={onTogglePause}
          className={`text-[10px] font-medium tracking-wider uppercase px-2.5 py-1 rounded-lg border transition ${
            isPaused
              ? "bg-red-500/15 border-red-500/30 text-red-400 hover:bg-red-500/25"
              : "bg-[#2E7D32]/10 border-[#2E7D32]/30 text-[#2E7D32] hover:bg-[#2E7D32]/20"
          }`}
        >
          {isPaused ? "Unpause" : "Pause"}
        </button>

        <button
          onClick={onDismiss}
          className="text-[10px] font-medium tracking-wider uppercase text-slate-500 bg-[#1E1E35] border border-[#1E1E35] px-2.5 py-1 rounded-lg hover:text-slate-300 hover:border-slate-500 transition"
        >
          Dismiss
        </button>

        <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [tab, setTab] = useState<"all" | "green" | "yellow" | "red">("all");
  const [users, setUsers] = useState<Assessment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [processing, setProcessing] = useState<ProcessingCard[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [highRiskFlash, setHighRiskFlash] = useState(false);
  const [bellBounce, setBellBounce] = useState(false);
  const [newCardId, setNewCardId] = useState<string | null>(null);
  const [seenIds, setSeenIds] = useState<Set<string>>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = sessionStorage.getItem("seenIds");
        return saved ? new Set(JSON.parse(saved)) : new Set();
      } catch { return new Set(); }
    }
    return new Set();
  });
  const [pastExpanded, setPastExpanded] = useState(true);
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

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === "analysis_started") {
          setProcessing((prev) => [
            {
              id: msg.data.id,
              user_id: msg.data.user_id,
              user_name: msg.data.user_name,
              agents: {},
              step: "Collecting user profile data",
            },
            ...prev,
          ]);
        } else if (msg.type === "agent_complete") {
          setProcessing((prev) =>
            prev.map((p) =>
              p.id === msg.data.id
                ? {
                    ...p,
                    agents: {
                      ...p.agents,
                      [msg.data.agent]: { score: msg.data.score, confidence: msg.data.confidence },
                    },
                    step: getStepLabel({
                      ...p.agents,
                      [msg.data.agent]: true,
                    }),
                  }
                : p
            )
          );
        } else if (msg.type === "analysis_complete") {
          const entry = msg.data.entry;
          setProcessing((prev) => prev.filter((p) => p.id !== msg.data.pending_id));

          if (entry && entry.cumulative_fraud_score >= 71) {
            setHighRiskFlash(true);
            setTimeout(() => setHighRiskFlash(false), 2000);
          }

          setBellBounce(true);
          setTimeout(() => setBellBounce(false), 600);

          if (entry) {
            setNewCardId(entry.id);
            setTimeout(() => setNewCardId(null), 800);
          }

          fetchData();
        } else if (msg.type === "pause_toggled") {
          fetchData();
        } else {
          fetchData();
        }
      } catch {
        fetchData();
      }
    };

    ws.onclose = () => setTimeout(() => fetchData(), 3000);

    return () => ws.close();
  }, [fetchData, router]);

  const filteredUsers =
    tab === "all" ? users : users.filter((u) => u.risk_level === tab);
  const unreadCount = alerts.filter((a) => !a.read).length;

  // Split into new and past
  const newCases = filteredUsers.filter((u) => !seenIds.has(u.id));
  const pastCases = filteredUsers.filter((u) => seenIds.has(u.id));

  // Stats
  const highCount = users.filter((u) => u.risk_level === "red").length;
  const medCount = users.filter((u) => u.risk_level === "yellow").length;
  const lowCount = users.filter((u) => u.risk_level === "green").length;
  const avgScore = users.length > 0
    ? Math.round(users.reduce((s, u) => s + u.cumulative_fraud_score, 0) / users.length)
    : 0;

  const markRead = async (id: string) => {
    await fetch(`/api/dashboard/alerts/${id}/read`, { method: "PATCH" });
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a))
    );
  };

  const togglePause = async (e: React.MouseEvent, userId: string) => {
    e.stopPropagation();
    await fetch(`/api/dashboard/users/${userId}/toggle-pause`, { method: "POST" });
    fetchData();
  };

  const dismissCase = async (e: React.MouseEvent, assessmentId: string) => {
    e.stopPropagation();
    await fetch(`/api/dashboard/assessments/${assessmentId}`, { method: "DELETE" });
    setUsers((prev) => prev.filter((u) => u.id !== assessmentId));
  };

  const navigateToCase = (user: Assessment) => {
    setSeenIds((prev) => {
      const next = new Set([...prev, user.id]);
      sessionStorage.setItem("seenIds", JSON.stringify([...next]));
      return next;
    });
    router.push(`/dashboard/user/${user.id}`);
  };

  return (
    <div className={`min-h-screen transition-all duration-500 ${highRiskFlash ? "ring-2 ring-red-500/50 ring-inset" : ""}`}>
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
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
            Live
          </div>

          {/* Notification Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifs(!showNotifs)}
              className={`relative p-2 rounded-lg hover:bg-[#0F0F1A] transition ${bellBounce ? "animate-bounce" : ""}`}
            >
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {unreadCount > 0 && (
                <span className={`absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full text-[9px] font-bold flex items-center justify-center text-white ${bellBounce ? "scale-125" : ""} transition-transform`}>
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
                  <p className="p-6 text-sm text-slate-600 text-center">No activity yet</p>
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
                              : "bg-[#2E7D32]"
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
        {/* Stats Strip */}
        {users.length > 0 && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Total Cases</p>
              <p className="text-2xl font-bold mt-1">{users.length}</p>
            </div>
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4">
              <p className="text-xs text-slate-500 uppercase tracking-wider">High Risk</p>
              <p className="text-2xl font-bold mt-1 text-red-400">{highCount}</p>
            </div>
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Medium Risk</p>
              <p className="text-2xl font-bold mt-1 text-amber-400">{medCount}</p>
            </div>
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Avg Score</p>
              <p className={`text-2xl font-bold mt-1 ${scoreText(avgScore)}`}>{avgScore}</p>
            </div>
          </div>
        )}

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
                {info.dot && <div className={`w-2 h-2 rounded-full ${info.dot}`} />}
                {info.label}
                <span className="text-xs opacity-60">({count})</span>
              </button>
            );
          })}
        </div>

        {/* Processing Cards */}
        {processing.length > 0 && (
          <div className="grid gap-3 mb-6">
            {processing.map((proc) => {
              const doneCount = Object.keys(proc.agents).length;
              return (
                <div
                  key={proc.id}
                  className="bg-gradient-to-r from-[#2E7D32]/10 to-[#2E7D32]/5 border border-[#2E7D32]/20 rounded-2xl p-5 cursor-default animate-[slideDown_0.4s_ease-out]"
                >
                  <div className="flex items-center gap-5">
                    <div className="relative shrink-0">
                      <svg className="w-14 h-14 -rotate-90 animate-spin" style={{ animationDuration: "3s" }} viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="15" fill="none" stroke="#1E1E35" strokeWidth="3" />
                        <circle
                          cx="18" cy="18" r="15" fill="none" stroke="#2E7D32" strokeWidth="3"
                          strokeDasharray={`${(doneCount / 6) * 94.2} 94.2`} strokeLinecap="round"
                        />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-[#2E7D32]">
                        {doneCount}/6
                      </span>
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-lg">{proc.user_name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-pulse" />
                        <p className="text-xs text-[#2E7D32] font-medium">{proc.step}</p>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mt-2.5">
                        {AGENT_ORDER.map((agent) => {
                          const result = proc.agents[agent.key];
                          const isDone = !!result;
                          return (
                            <span
                              key={agent.key}
                              className={`text-[10px] px-2 py-0.5 rounded-md border transition-all duration-500 ${
                                isDone
                                  ? "bg-[#2E7D32]/15 border-[#2E7D32]/30 text-[#2E7D32]"
                                  : "bg-[#1E1E35]/50 border-[#1E1E35] text-slate-600"
                              }`}
                            >
                              {agent.label}: {isDone ? `${result.score}` : "..."}
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    <span className="text-[10px] font-medium tracking-wider uppercase text-[#2E7D32] bg-[#2E7D32]/10 px-2.5 py-1 rounded-lg border border-[#2E7D32]/20 shrink-0">
                      Analyzing
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Empty state */}
        {filteredUsers.length === 0 && processing.length === 0 ? (
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
          <>
            {/* NEW section */}
            {newCases.length > 0 && (
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
                  <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
                    New
                  </h2>
                  <span className="text-xs text-slate-500">({newCases.length})</span>
                  <div className="flex-1 h-px bg-[#1E1E35]" />
                </div>
                <div className="grid gap-3">
                  {newCases.map((user) => (
                    <CaseCard
                      key={user.id}
                      user={user}
                      isNew={newCardId === user.id}
                      onNavigate={() => navigateToCase(user)}
                      onTogglePause={(e) => togglePause(e, user.user_id)}
                      onDismiss={(e) => dismissCase(e, user.id)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* PAST section */}
            {pastCases.length > 0 && (
              <div>
                <button
                  onClick={() => setPastExpanded(!pastExpanded)}
                  className="flex items-center gap-3 mb-4 w-full group"
                >
                  <svg
                    className={`w-3 h-3 text-slate-500 transition-transform ${pastExpanded ? "rotate-90" : ""}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 group-hover:text-slate-300 transition">
                    Reviewed
                  </h2>
                  <span className="text-xs text-slate-600">({pastCases.length})</span>
                  <div className="flex-1 h-px bg-[#1E1E35]" />
                </button>
                {pastExpanded && (
                  <div className="grid gap-3">
                    {pastCases.map((user) => (
                      <CaseCard
                        key={user.id}
                        user={user}
                        isNew={false}
                        onNavigate={() => navigateToCase(user)}
                        onTogglePause={(e) => togglePause(e, user.user_id)}
                        onDismiss={(e) => dismissCase(e, user.id)}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <style jsx global>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
