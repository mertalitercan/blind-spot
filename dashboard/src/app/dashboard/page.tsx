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
  amount?: number;
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

interface DashboardStats {
  critical_alerts: number;
  flagged_today: number;
  blocked_value: number;
  accounts_paused: number;
}

interface AgentChatMessage {
  role: "user" | "assistant";
  content: string;
}

const AGENT_ORDER = [
  { key: "behavioral", label: "Behavioral" },
  { key: "cognitive", label: "Cognitive" },
  { key: "transaction", label: "Transaction" },
  { key: "device", label: "Device" },
  { key: "graph", label: "Graph" },
  { key: "metascorer", label: "Meta-Scorer" },
];

const SIDEBAR_AGENTS = [
  {
    key: "behavioral",
    label: "Behavioral",
    intro:
      "Hi, I'm the Behavioral Biometrics Agent. I analyze typing patterns, touch dynamics, and navigation behavior to detect deviations from a user's established baseline. Ask me about keystroke analysis, touch pressure anomalies, or session navigation patterns.",
  },
  {
    key: "cognitive",
    label: "Cognitive",
    intro:
      "Hi, I'm the Cognitive State Agent. I specialize in detecting psychological manipulation \u2014 coercion, coached behavior, and stress patterns during banking sessions. Ask me about phone call indicators, segmented typing, or dead time analysis.",
  },
  {
    key: "transaction",
    label: "Transaction",
    intro:
      "Hi, I'm the Transaction Pattern Agent. I analyze financial patterns including amount anomalies, velocity checks, recipient history, and temporal patterns. Ask me about z-scores, transaction velocity, or pattern detection.",
  },
  {
    key: "device",
    label: "Device",
    intro:
      "Hi, I'm the Device & Network Agent. I monitor device fingerprints, network characteristics, VPN/proxy detection, and session context. Ask me about device recognition, remote access detection, or network anomalies.",
  },
  {
    key: "graph",
    label: "Graph",
    intro:
      "Hi, I'm the Graph Intelligence Agent. I analyze the network of relationships between accounts to detect organized fraud patterns like fan-in, fan-out, circular transfers, and mule networks. Ask me about transaction graph analysis.",
  },
];

function getStepLabel(agents: Record<string, any>): string {
  const done = Object.keys(agents);
  if (done.includes("metascorer")) return "Finalizing assessment";
  if (done.includes("graph") || done.includes("device")) {
    if (done.includes("graph") && done.includes("device"))
      return "Running meta-reasoning synthesis";
    return "Analyzing device & network data";
  }
  if (done.length >= 1) return "Analyzing behavior, cognition & transaction";
  return "Collecting user profile data";
}

const TAB_STYLES: Record<
  string,
  { active: string; dot: string; label: string }
> = {
  all: {
    active: "border-[#2E7D32] text-[#2E7D32]",
    dot: "",
    label: "All Cases",
  },
  red: {
    active: "border-red-400 text-red-300",
    dot: "bg-red-400",
    label: "High Risk",
  },
  yellow: {
    active: "border-amber-400 text-amber-300",
    dot: "bg-amber-400",
    label: "Medium",
  },
  green: {
    active: "border-[#2E7D32] text-[#2E7D32]",
    dot: "bg-[#2E7D32]",
    label: "Low Risk",
  },
};

function scoreGradient(score: number) {
  if (score >= 71) return "from-red-500/20 to-red-500/5 border-red-500/20";
  if (score >= 31)
    return "from-amber-500/20 to-amber-500/5 border-amber-500/20";
  return "from-[#2E7D32]/20 to-[#2E7D32]/5 border-[#2E7D32]/20";
}

function scoreText(score: number) {
  if (score >= 71) return "text-red-400";
  if (score >= 31) return "text-amber-400";
  return "text-[#2E7D32]";
}

/* ── SVG Icon Components ── */

function IconDashboard({ active }: { active?: boolean }) {
  return (
    <svg
      className={`w-5 h-5 ${active ? "text-[#2E7D32]" : "text-slate-500"}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
      />
    </svg>
  );
}

function IconAlerts({ active }: { active?: boolean }) {
  return (
    <svg
      className={`w-5 h-5 ${active ? "text-[#2E7D32]" : "text-slate-500"}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
      />
    </svg>
  );
}

function IconFingerprint() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"
      />
    </svg>
  );
}

function IconBrain() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
      />
    </svg>
  );
}

function IconDollar() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function IconDevice() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
      />
    </svg>
  );
}

function IconGraph() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
      />
    </svg>
  );
}

function IconSignOut() {
  return (
    <svg
      className="w-5 h-5 text-slate-600"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
      />
    </svg>
  );
}

const AGENT_ICONS: Record<string, () => React.ReactElement> = {
  behavioral: IconFingerprint,
  cognitive: IconBrain,
  transaction: IconDollar,
  device: IconDevice,
  graph: IconGraph,
};

/* ── Case Card ── */

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
                  : "#2E7D32"
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
          {isPaused && (
            <p className="text-xs text-red-300/80 mt-0.5 line-clamp-1 max-w-md">
              Account paused &mdash;{" "}
              {user.assessment?.meta?.reasoning?.split(".")[0] ||
                "Suspicious activity detected"}
              .
            </p>
          )}
          <p className="text-xs text-slate-500 mt-0.5">
            {user.user_id} &middot;{" "}
            {new Date(user.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
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
  );
}

/* ── Agent Chat Popup ── */

function AgentChatPopup({
  agent,
  onClose,
}: {
  agent: (typeof SIDEBAR_AGENTS)[0];
  onClose: () => void;
}) {
  const [messages, setMessages] = useState<AgentChatMessage[]>([
    { role: "assistant", content: agent.intro },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    const updated: AgentChatMessage[] = [
      ...messages,
      { role: "user", content: q },
    ];
    setMessages(updated);
    setLoading(true);

    try {
      const res = await fetch("/api/dashboard/agent-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: agent.key,
          question: q,
          history: updated.slice(1).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });
      const data = await res.json();
      setMessages([
        ...updated,
        { role: "assistant", content: data.response },
      ]);
    } catch {
      setMessages([
        ...updated,
        {
          role: "assistant",
          content: "Error connecting to backend. Is it running?",
        },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="fixed bottom-6 right-6 w-[380px] h-[500px] bg-[#0A0A15] border border-[#1E1E35] rounded-2xl shadow-2xl shadow-black/60 flex flex-col z-50 animate-[slideUp_0.3s_ease-out]">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#1E1E35] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
          <span className="text-sm font-semibold">{agent.label} Agent</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-[#1E1E35] transition"
        >
          <svg
            className="w-4 h-4 text-slate-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`text-[13px] rounded-xl p-3 ${
              msg.role === "user"
                ? "bg-[#2E7D32]/10 border border-[#2E7D32]/20 ml-8"
                : "bg-[#0F0F1A] border border-[#1E1E35] mr-8"
            }`}
          >
            <p className="whitespace-pre-wrap leading-relaxed text-slate-300">
              {msg.content}
            </p>
          </div>
        ))}
        {loading && (
          <div className="bg-[#0F0F1A] border border-[#1E1E35] mr-8 rounded-xl p-3">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce" />
              <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:150ms]" />
              <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-[#1E1E35] shrink-0">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder={`Ask ${agent.label} Agent...`}
            className="flex-1 bg-[#050510] border border-[#1E1E35] rounded-xl px-3 py-2 text-sm outline-none focus:border-[#2E7D32]/50 transition placeholder:text-slate-700"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="bg-[#2E7D32] disabled:opacity-30 rounded-xl px-4 py-2 text-sm font-medium transition hover:bg-[#256d29]"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main Dashboard ── */

export default function DashboardPage() {
  const [tab, setTab] = useState<"all" | "green" | "yellow" | "red">("all");
  const [users, setUsers] = useState<Assessment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    critical_alerts: 0,
    flagged_today: 0,
    blocked_value: 0,
    accounts_paused: 0,
  });
  const [processing, setProcessing] = useState<ProcessingCard[]>([]);
  const [highRiskFlash, setHighRiskFlash] = useState(false);
  const [bellBounce, setBellBounce] = useState(false);
  const [newCardId, setNewCardId] = useState<string | null>(null);
  const [seenIds, setSeenIds] = useState<Set<string>>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = sessionStorage.getItem("seenIds");
        return saved ? new Set(JSON.parse(saved)) : new Set();
      } catch {
        return new Set();
      }
    }
    return new Set();
  });
  const [pastExpanded, setPastExpanded] = useState(true);

  // Sidebar state
  const [showAlertsPanel, setShowAlertsPanel] = useState(false);
  const [activeAgent, setActiveAgent] = useState<
    (typeof SIDEBAR_AGENTS)[0] | null
  >(null);

  const wsRef = useRef<WebSocket | null>(null);
  const router = useRouter();

  const fetchData = useCallback(async () => {
    try {
      const [usersRes, alertsRes, statsRes] = await Promise.all([
        fetch("/api/dashboard/users"),
        fetch("/api/dashboard/alerts"),
        fetch("/api/dashboard/stats"),
      ]);
      setUsers(await usersRes.json());
      setAlerts(await alertsRes.json());
      setStats(await statsRes.json());
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
                      [msg.data.agent]: {
                        score: msg.data.score,
                        confidence: msg.data.confidence,
                      },
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
          setProcessing((prev) =>
            prev.filter((p) => p.id !== msg.data.pending_id)
          );

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

  const newCases = filteredUsers.filter((u) => !seenIds.has(u.id));
  const pastCases = filteredUsers.filter((u) => seenIds.has(u.id));

  const markRead = async (id: string) => {
    await fetch(`/api/dashboard/alerts/${id}/read`, { method: "PATCH" });
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a))
    );
  };

  const togglePause = async (e: React.MouseEvent, userId: string) => {
    e.stopPropagation();
    await fetch(`/api/dashboard/users/${userId}/toggle-pause`, {
      method: "POST",
    });
    fetchData();
  };

  const dismissCase = async (e: React.MouseEvent, assessmentId: string) => {
    e.stopPropagation();
    await fetch(`/api/dashboard/assessments/${assessmentId}`, {
      method: "DELETE",
    });
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
    <div
      className={`flex min-h-screen transition-all duration-500 ${
        highRiskFlash ? "ring-2 ring-red-500/50 ring-inset" : ""
      }`}
    >
      {/* ── Sidebar ── */}
      <aside className="w-16 border-r border-[#1E1E35] flex flex-col items-center py-5 shrink-0 bg-[#050510] z-40">
        {/* Spacer for top */}
        <div className="mb-8 h-8" />

        {/* Dashboard */}
        <button
          onClick={() => setShowAlertsPanel(false)}
          className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2 transition group relative ${
            !showAlertsPanel
              ? "bg-[#2E7D32]/10 border border-[#2E7D32]/20"
              : "hover:bg-[#0F0F1A]"
          }`}
        >
          <IconDashboard active={!showAlertsPanel} />
          <span className="absolute left-14 bg-[#1E1E35] text-xs text-slate-300 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-50">
            Dashboard
          </span>
        </button>

        {/* Alerts */}
        <button
          onClick={() => setShowAlertsPanel(!showAlertsPanel)}
          className={`w-10 h-10 rounded-xl flex items-center justify-center mb-6 transition group relative ${
            showAlertsPanel
              ? "bg-[#2E7D32]/10 border border-[#2E7D32]/20"
              : "hover:bg-[#0F0F1A]"
          }`}
        >
          <IconAlerts active={showAlertsPanel} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-3.5 h-3.5 bg-red-500 rounded-full text-[8px] font-bold flex items-center justify-center text-white">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
          <span className="absolute left-14 bg-[#1E1E35] text-xs text-slate-300 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-50">
            Alerts
          </span>
        </button>

        {/* Divider */}
        <div className="w-6 h-px bg-[#1E1E35] mb-4" />
        <span className="text-[8px] text-slate-600 uppercase tracking-widest mb-3">
          Agents
        </span>

        {/* Agent buttons */}
        {SIDEBAR_AGENTS.map((agent) => {
          const Icon = AGENT_ICONS[agent.key];
          const isActive = activeAgent?.key === agent.key;
          return (
            <button
              key={agent.key}
              onClick={() => setActiveAgent(isActive ? null : agent)}
              className={`w-10 h-10 rounded-xl flex items-center justify-center mb-1.5 transition group relative ${
                isActive
                  ? "bg-[#2E7D32]/10 border border-[#2E7D32]/20 text-[#2E7D32]"
                  : "hover:bg-[#0F0F1A] text-slate-500"
              }`}
            >
              <Icon />
              <span className="absolute left-14 bg-[#1E1E35] text-xs text-slate-300 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-50">
                {agent.label}
              </span>
            </button>
          );
        })}

        {/* Spacer + Sign out */}
        <div className="flex-1" />
        <button
          onClick={() => {
            sessionStorage.removeItem("authed");
            router.push("/");
          }}
          className="w-10 h-10 rounded-xl flex items-center justify-center hover:bg-[#0F0F1A] transition group relative"
        >
          <IconSignOut />
          <span className="absolute left-14 bg-[#1E1E35] text-xs text-slate-300 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-50">
            Sign out
          </span>
        </button>
      </aside>

      {/* ── Alerts Panel ── */}
      {showAlertsPanel && (
        <div className="w-80 border-r border-[#1E1E35] bg-[#0A0A15] flex flex-col shrink-0 animate-[slideRight_0.2s_ease-out]">
          <div className="px-4 py-4 border-b border-[#1E1E35] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Alerts</h2>
              <p className="text-xs text-slate-600 mt-0.5">
                {unreadCount} unread
              </p>
            </div>
            <button
              onClick={() => setShowAlertsPanel(false)}
              className="p-1 rounded-lg hover:bg-[#1E1E35] transition"
            >
              <svg
                className="w-4 h-4 text-slate-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="p-6 text-sm text-slate-600 text-center">
                No alerts yet
              </p>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  onClick={() => markRead(alert.id)}
                  className={`px-4 py-3 border-b border-[#1E1E35]/50 cursor-pointer hover:bg-[#0F0F1A] transition ${
                    !alert.read ? "bg-[#0F0F1A]" : ""
                  }`}
                >
                  <div className="flex items-start gap-2.5">
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
                      <p className="text-[13px] leading-relaxed text-slate-300">
                        {alert.message}
                      </p>
                      <p className="text-[11px] text-slate-600 mt-1">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="border-b border-[#1E1E35] px-8 py-5 flex items-center justify-between shrink-0">
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
            <button
              onClick={() => { sessionStorage.removeItem("authed"); router.push("/"); }}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition px-3 py-1.5 rounded-lg hover:bg-[#1E1E35]"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </header>

        <div className="p-8 flex-1 overflow-y-auto max-w-7xl mx-auto w-full">
          {/* Stats Strip */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-slate-500 uppercase tracking-wider">
                  Critical Alerts
                </p>
                <div className="w-6 h-6 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <svg
                    className="w-3.5 h-3.5 text-red-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-red-400">
                {stats.critical_alerts}
              </p>
            </div>

            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-slate-500 uppercase tracking-wider">
                  Flagged Today
                </p>
                <div className="w-6 h-6 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <svg
                    className="w-3.5 h-3.5 text-amber-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"
                    />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-amber-400">
                {stats.flagged_today}
              </p>
            </div>

            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-slate-500 uppercase tracking-wider">
                  Blocked Value
                </p>
                <div className="w-6 h-6 rounded-lg bg-[#2E7D32]/10 flex items-center justify-center">
                  <svg
                    className="w-3.5 h-3.5 text-[#2E7D32]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-[#2E7D32]">
                $
                {stats.blocked_value >= 1000
                  ? `${(stats.blocked_value / 1000).toFixed(1)}k`
                  : stats.blocked_value.toFixed(0)}
              </p>
            </div>

            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-4 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-slate-500 uppercase tracking-wider">
                  Accounts Paused
                </p>
                <div className="w-6 h-6 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <svg
                    className="w-3.5 h-3.5 text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-blue-400">
                {stats.accounts_paused}
              </p>
            </div>
          </div>

          {/* Agent Performance + Fraud Type Distribution */}
          {(() => {
            // Compute agent performance
            const agentKeys = [
              { key: "behavioral", label: "Behavioral", scoreKey: "risk_score" },
              { key: "cognitive", label: "Cognitive", scoreKey: "cognitive_risk_score" },
              { key: "transaction", label: "Transaction", scoreKey: "risk_score" },
              { key: "device", label: "Device", scoreKey: "risk_score" },
              { key: "graph", label: "Graph", scoreKey: "risk_score" },
            ];
            const agentPerf = agentKeys.map((agent) => {
              const agentDataList = users
                .map((u) => u.assessment?.[agent.key])
                .filter((d): d is any => d !== undefined && d !== null);
              const scores = agentDataList
                .map((d) => d[agent.scoreKey] as number | undefined)
                .filter((s): s is number => s !== undefined && s !== null);
              const avg = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
              const highCount = scores.filter((s) => s >= 71).length;
              const medCount = scores.filter((s) => s >= 31 && s < 71).length;
              const detectionRate = scores.length > 0 ? Math.round(((highCount + medCount) / scores.length) * 100) : 0;
              // Collect all flags across assessments
              const allFlags: Record<string, number> = {};
              agentDataList.forEach((d) => {
                const flags: string[] = d.flags || d.coercion_indicators || [];
                flags.forEach((f: string) => { allFlags[f] = (allFlags[f] || 0) + 1; });
              });
              const topFlags = Object.entries(allFlags)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 2)
                .map(([flag]) => flag);
              // Check if this agent was the highest scorer in any assessment
              let primaryCount = 0;
              users.forEach((u) => {
                const a = u.assessment;
                if (!a) return;
                const thisScore = a[agent.key]?.[agent.scoreKey] ?? 0;
                const otherMax = agentKeys
                  .filter((ak) => ak.key !== agent.key)
                  .map((ak) => a[ak.key]?.[ak.scoreKey] ?? 0)
                  .reduce((m, s) => Math.max(m, s as number), 0);
                if (thisScore > 0 && thisScore >= otherMax) primaryCount++;
              });
              return { ...agent, avg, highCount, medCount, detectionRate, topFlags, primaryCount, total: scores.length };
            });

            // Compute fraud type distribution
            const fraudTotals: Record<string, number> = {};
            let fraudCount = 0;
            users.forEach((u) => {
              const fta = u.assessment?.meta?.fraud_type_assessment;
              if (fta) {
                fraudCount++;
                Object.entries(fta).forEach(([key, val]) => {
                  fraudTotals[key] = (fraudTotals[key] || 0) + (val as number);
                });
              }
            });
            const defaultTypes = ["authorized_push_payment", "account_takeover", "money_mule", "legitimate"];
            const fraudAvgs = fraudCount > 0
              ? Object.entries(fraudTotals)
                  .map(([key, total]) => ({ key, avg: total / fraudCount }))
                  .sort((a, b) => b.avg - a.avg)
              : defaultTypes.map((key) => ({ key, avg: key === "legitimate" ? 1 : 0 }));
            const fraudTotal = fraudAvgs.reduce((s, f) => s + f.avg, 0) || 1;

            const fraudColors: Record<string, string> = {
              authorized_push_payment: "#f87171",
              account_takeover: "#fbbf24",
              money_mule: "#60a5fa",
              legitimate: "#2E7D32",
            };

            // SVG donut segments
            const radius = 40;
            const circumference = 2 * Math.PI * radius;
            let cumulativeOffset = 0;
            const segments = fraudAvgs.map((f) => {
              const pct = f.avg / fraudTotal;
              const dashLen = pct * circumference;
              const offset = cumulativeOffset;
              cumulativeOffset += dashLen;
              return { ...f, pct, dashLen, offset, color: fraudColors[f.key] || "#64748b" };
            });

            return (
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-8">
                {/* Agent Decision Factors */}
                <div className="lg:col-span-3 bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl px-4 py-5 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-300">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-blue-400" />
                    <p className="text-sm font-semibold">Threat Signal Breakdown</p>
                  </div>
                  <p className="text-[11px] text-slate-600 mb-5 ml-4">Which agents are detecting the most risk across all cases</p>
                  <div className="flex items-center justify-center gap-6">
                    {agentPerf.map((agent) => {
                      const scoreColor = agent.avg >= 71 ? "text-red-400" : agent.avg >= 31 ? "text-amber-400" : "text-[#2E7D32]";
                      const ringColor = agent.avg >= 71 ? "#f87171" : agent.avg >= 31 ? "#fbbf24" : "#2E7D32";
                      const glowColor = agent.avg >= 71 ? "rgba(248,113,113,0.15)" : agent.avg >= 31 ? "rgba(251,191,36,0.15)" : "rgba(46,125,50,0.15)";
                      return (
                        <div key={agent.key} className="flex flex-col items-center gap-2 cursor-default group">
                          <div
                            className="relative transition-all duration-300 group-hover:scale-110"
                            style={{ filter: "drop-shadow(0 0 0px transparent)" }}
                            onMouseEnter={(e) => e.currentTarget.style.filter = `drop-shadow(0 0 8px ${glowColor})`}
                            onMouseLeave={(e) => e.currentTarget.style.filter = "drop-shadow(0 0 0px transparent)"}
                          >
                            <svg className="w-20 h-20 -rotate-90" viewBox="0 0 36 36">
                              <circle cx="18" cy="18" r="14" fill="none" stroke="#1E1E35" strokeWidth="2.5" />
                              <circle cx="18" cy="18" r="14" fill="none" stroke={ringColor} strokeWidth="2.5"
                                strokeDasharray={`${(agent.avg / 100) * 88} 88`} strokeLinecap="round" />
                            </svg>
                            <span className={`absolute inset-0 flex items-center justify-center text-base font-bold ${scoreColor}`}>{agent.avg}</span>
                          </div>
                          <span className="text-[11px] text-slate-500 group-hover:text-slate-200 transition-colors duration-300">{agent.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Fraud Type Distribution */}
                <div className="lg:col-span-2 bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl px-4 py-5 hover:border-[#2A2A45] hover:bg-[#111122] transition-all duration-300">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-2 h-2 rounded-full bg-blue-400" />
                    <p className="text-sm font-semibold">Fraud Distribution</p>
                  </div>
                  <div className="flex items-center gap-6">
                    {/* Donut */}
                    <div className="relative shrink-0 group cursor-default">
                      <div className="transition-transform duration-300 group-hover:scale-105">
                        <svg className="w-28 h-28" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r={radius} fill="none" stroke="#1E1E35" strokeWidth="10" />
                          {segments.map((seg) => (
                            <circle
                              key={seg.key}
                              cx="50" cy="50" r={radius}
                              fill="none"
                              stroke={seg.color}
                              strokeWidth="10"
                              strokeDasharray={`${seg.dashLen} ${circumference - seg.dashLen}`}
                              strokeDashoffset={-seg.offset}
                              strokeLinecap="butt"
                              transform="rotate(-90 50 50)"
                              className="transition-all duration-700 hover:opacity-80"
                            />
                          ))}
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-lg font-bold text-slate-200">{users.length}</span>
                          <span className="text-[9px] text-slate-600">cases</span>
                        </div>
                      </div>
                    </div>
                    {/* Legend */}
                    <div className="space-y-2.5 flex-1">
                      {segments.map((seg) => (
                        <div key={seg.key} className="flex items-center gap-2.5 group/item cursor-default rounded-lg px-2 py-1 -mx-2 hover:bg-[#1E1E35]/50 transition-all duration-200">
                          <div className="w-2.5 h-2.5 rounded-sm shrink-0 transition-transform duration-200 group-hover/item:scale-125" style={{ backgroundColor: seg.color }} />
                          <span className="text-xs text-slate-400 capitalize flex-1 group-hover/item:text-slate-200 transition-colors duration-200">{seg.key.replace(/_/g, " ")}</span>
                          <span className="text-xs font-mono font-medium transition-all duration-200 group-hover/item:text-sm" style={{ color: seg.color }}>
                            {Math.round(seg.pct * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}

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
                        <svg
                          className="w-14 h-14 -rotate-90 animate-spin"
                          style={{ animationDuration: "3s" }}
                          viewBox="0 0 36 36"
                        >
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
                            stroke="#2E7D32"
                            strokeWidth="3"
                            strokeDasharray={`${
                              (doneCount / 6) * 94.2
                            } 94.2`}
                            strokeLinecap="round"
                          />
                        </svg>
                        <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-[#2E7D32]">
                          {doneCount}/6
                        </span>
                      </div>

                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-lg">
                          {proc.user_name}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-pulse" />
                          <p className="text-xs text-[#2E7D32] font-medium">
                            {proc.step}
                          </p>
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
              <p className="text-slate-500 text-lg font-light">
                No flagged users
              </p>
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
                    <span className="text-xs text-slate-500">
                      ({newCases.length})
                    </span>
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
                      className={`w-3 h-3 text-slate-500 transition-transform ${
                        pastExpanded ? "rotate-90" : ""
                      }`}
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
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 group-hover:text-slate-300 transition">
                      Reviewed
                    </h2>
                    <span className="text-xs text-slate-600">
                      ({pastCases.length})
                    </span>
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
      </main>

      {/* ── Agent Chat Popup ── */}
      {activeAgent && (
        <AgentChatPopup
          agent={activeAgent}
          onClose={() => setActiveAgent(null)}
        />
      )}

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
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slideRight {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}
