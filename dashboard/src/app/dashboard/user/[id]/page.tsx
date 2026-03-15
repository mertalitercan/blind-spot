"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";

interface AgentData {
  risk_score?: number;
  cognitive_risk_score?: number;
  cumulative_fraud_score?: number;
  confidence?: number;
  flags?: string[];
  reasoning?: string;
  detected_state?: string;
  coercion_indicators?: string[];
  stress_indicators?: string[];
  coached_indicators?: string[];
  risk_level?: string;
  recommended_actions?: string[];
  fraud_type_assessment?: Record<string, number>;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const AGENTS = [
  { key: "behavioral", label: "Behavioral", scoreKey: "risk_score", icon: "fingerprint" },
  { key: "cognitive", label: "Cognitive", scoreKey: "cognitive_risk_score", icon: "brain" },
  { key: "transaction", label: "Transaction", scoreKey: "risk_score", icon: "dollar" },
  { key: "device", label: "Device", scoreKey: "risk_score", icon: "device" },
  { key: "graph", label: "Graph", scoreKey: "risk_score", icon: "graph" },
  { key: "meta", label: "Overall", scoreKey: "cumulative_fraud_score", icon: "shield" },
];

function scoreColor(s: number) {
  if (s >= 71) return "text-red-400";
  if (s >= 31) return "text-amber-400";
  return "text-[#2E7D32]";
}

function barColor(s: number) {
  if (s >= 71) return "bg-red-400";
  if (s >= 31) return "bg-amber-400";
  return "bg-[#2E7D32]";
}

export default function UserDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("authed") !== "true") {
      router.push("/");
      return;
    }
    fetch(`/api/dashboard/assessments/${id}`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => {});
  }, [id, router]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const sendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const question = chatInput.trim();
    setChatInput("");
    const updated: ChatMessage[] = [
      ...chatMessages,
      { role: "user", content: question },
    ];
    setChatMessages(updated);
    setChatLoading(true);

    try {
      const res = await fetch("/api/dashboard/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          assessment: data?.assessment || {},
          history: updated.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });
      const result = await res.json();
      setChatMessages([
        ...updated,
        { role: "assistant", content: result.response },
      ]);
    } catch {
      setChatMessages([
        ...updated,
        {
          role: "assistant",
          content: "Error connecting to AI. Is the backend running?",
        },
      ]);
    }
    setChatLoading(false);
  };

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
          <span className="text-slate-500">Loading case...</span>
        </div>
      </div>
    );
  }

  const assessment = data.assessment || {};
  const meta = assessment.meta || {};
  const finalScore = meta.cumulative_fraud_score || 0;

  return (
    <div className="min-h-screen">
      {/* Top Bar */}
      <header className="border-b border-[#1E1E35] px-8 py-4 flex items-center gap-5">
        <button
          onClick={() => router.push("/dashboard")}
          className="p-2 rounded-xl hover:bg-[#0F0F1A] transition"
        >
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="font-semibold text-lg">{data.user_name}</h1>
            <span className={`text-xs font-medium tracking-wider uppercase ${scoreColor(finalScore)}`}>
              {finalScore >= 71 ? "HIGH RISK" : finalScore >= 31 ? "MEDIUM RISK" : "LOW RISK"}
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-0.5">
            {data.user_id} · {new Date(data.timestamp).toLocaleString()}
          </p>
        </div>
      </header>

      <div className="p-8 grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Left: Scores + Analysis (3 cols) */}
        <div className="lg:col-span-3 space-y-6">
          {/* Score Hero */}
          <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-8 flex items-center gap-8">
            <div className="relative shrink-0">
              <svg className="w-28 h-28 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15" fill="none" stroke="#1E1E35" strokeWidth="2.5" />
                <circle
                  cx="18" cy="18" r="15" fill="none"
                  stroke={finalScore >= 71 ? "#f87171" : finalScore >= 31 ? "#fbbf24" : "#2E7D32"}
                  strokeWidth="2.5"
                  strokeDasharray={`${(finalScore / 100) * 94.2} 94.2`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-3xl font-bold ${scoreColor(finalScore)}`}>{finalScore}</span>
                <span className="text-[10px] text-slate-600">/100</span>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm text-slate-500 mb-1">Final Assessment</p>
              <p className="text-sm text-slate-300 leading-relaxed">
                {meta.reasoning || "No meta reasoning available."}
              </p>
              {meta.recommended_actions && meta.recommended_actions.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {meta.recommended_actions.slice(0, 3).map((a: string, i: number) => (
                    <span key={i} className="text-[10px] bg-[#1E1E35] text-slate-400 px-2.5 py-1 rounded-lg">
                      {a}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Agent Cards */}
          <div className="space-y-2">
            {AGENTS.map((agent) => {
              const agentData: AgentData = assessment[agent.key] || {};
              const score = (agentData as any)[agent.scoreKey] || 0;
              const isExpanded = expandedAgent === agent.key;

              return (
                <div
                  key={agent.key}
                  className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedAgent(isExpanded ? null : agent.key)}
                    className="w-full p-4 flex items-center gap-4 hover:bg-[#141425] transition"
                  >
                    <div className="w-10 h-10 rounded-xl bg-[#1E1E35] flex items-center justify-center shrink-0">
                      <span className={`text-sm font-bold ${scoreColor(score)}`}>{score}</span>
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-medium">{agent.label}</p>
                      <div className="w-full h-1.5 bg-[#1E1E35] rounded-full mt-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${barColor(score)} transition-all duration-500`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-xs text-slate-600">
                      {((agentData.confidence || 0) * 100).toFixed(0)}% conf
                    </span>
                    <svg
                      className={`w-4 h-4 text-slate-600 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {isExpanded && (
                    <div className="px-5 pb-5 border-t border-[#1E1E35]">
                      {agentData.reasoning && (
                        <p className="text-sm text-slate-400 mt-4 leading-relaxed">
                          {agentData.reasoning}
                        </p>
                      )}
                      {agentData.flags && agentData.flags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3">
                          {agentData.flags.map((f, i) => (
                            <span
                              key={i}
                              className="text-[10px] bg-red-500/10 text-red-300 border border-red-500/20 px-2 py-0.5 rounded-md"
                            >
                              {f}
                            </span>
                          ))}
                        </div>
                      )}
                      {agentData.detected_state && (
                        <p className="text-xs text-slate-500 mt-3">
                          State: <span className="text-slate-300">{agentData.detected_state}</span>
                        </p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Fraud Type */}
          {meta.fraud_type_assessment && (
            <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-5">
              <p className="text-sm font-medium mb-4 text-slate-400">Fraud Type Probability</p>
              <div className="space-y-3">
                {Object.entries(meta.fraud_type_assessment).map(([type, prob]) => (
                  <div key={type} className="flex items-center gap-4">
                    <span className="text-xs text-slate-500 w-44 capitalize">
                      {type.replace(/_/g, " ")}
                    </span>
                    <div className="flex-1 h-1.5 bg-[#1E1E35] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${barColor((prob as number) * 100)}`}
                        style={{ width: `${(prob as number) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-slate-400 w-10 text-right">
                      {((prob as number) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: AI Chat (2 cols) */}
        <div className="lg:col-span-2">
          <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl flex flex-col h-[calc(100vh-130px)] sticky top-8">
            <div className="p-5 border-b border-[#1E1E35]">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
                <h3 className="font-semibold text-sm">BlindSpot AI</h3>
              </div>
              <p className="text-xs text-slate-600 mt-1">
                Investigate this case with AI assistance
              </p>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {chatMessages.length === 0 && (
                <div className="py-8">
                  <p className="text-slate-600 text-sm text-center mb-5">
                    Ask about this flagged case
                  </p>
                  <div className="space-y-2">
                    {[
                      "Why was this person flagged?",
                      "What are the strongest fraud indicators?",
                      "Could this be a false positive?",
                      "What action should we take?",
                    ].map((q) => (
                      <button
                        key={q}
                        onClick={() => setChatInput(q)}
                        className="block w-full text-left text-xs bg-[#141425] hover:bg-[#1E1E35] border border-[#1E1E35] rounded-xl px-4 py-2.5 transition text-slate-400"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {chatMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`text-sm rounded-2xl p-4 ${
                    msg.role === "user"
                      ? "bg-[#2E7D32]/10 border border-[#2E7D32]/20 ml-6"
                      : "bg-[#141425] border border-[#1E1E35] mr-6"
                  }`}
                >
                  <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2">
                    {msg.role === "user" ? "You" : "BlindSpot AI"}
                  </p>
                  <p className="whitespace-pre-wrap leading-relaxed text-slate-300">
                    {msg.content}
                  </p>
                </div>
              ))}

              {chatLoading && (
                <div className="bg-[#141425] border border-[#1E1E35] mr-6 rounded-2xl p-4">
                  <p className="text-[10px] uppercase tracking-wider text-slate-600 mb-2">
                    BlindSpot AI
                  </p>
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce" />
                    <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:150ms]" />
                    <div className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-[#1E1E35]">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendChat()}
                  placeholder="Ask about this case..."
                  className="flex-1 bg-[#050510] border border-[#1E1E35] rounded-xl px-4 py-2.5 text-sm outline-none focus:border-[#2E7D32]/50 transition placeholder:text-slate-700"
                />
                <button
                  onClick={sendChat}
                  disabled={chatLoading || !chatInput.trim()}
                  className="bg-[#2E7D32] hover:bg-[#2E7D32] disabled:opacity-30 rounded-xl px-5 py-2.5 text-sm font-medium transition"
                >
                  Ask
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
