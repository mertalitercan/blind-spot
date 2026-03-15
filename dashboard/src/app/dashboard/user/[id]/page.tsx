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
      <header className="border-b border-[#1E1E35] px-8 py-4 flex items-center gap-5 max-w-6xl mx-auto">
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

      <div className="p-8 space-y-8 max-w-6xl mx-auto">
        {/* Main content: Info (left) + Chat (right) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Left: Scores + Analysis */}
          <div className="lg:col-span-2 space-y-6">
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

            {/* Cognitive State Card */}
            {(() => {
              const cog = assessment.cognitive;
              if (!cog) return null;
              const state: string = cog.detected_state || "normal";
              const confidence: number = cog.confidence || 0;
              const coercion: string[] = cog.coercion_indicators || [];
              const stress: string[] = cog.stress_indicators || [];
              const coached: string[] = cog.coached_indicators || [];
              const allStress = [...stress, ...coached];

              if (state === "normal" && coercion.length === 0 && allStress.length === 0) return null;

              const isHigh = state === "coercion_likely" || state === "coaching_suspected" || state === "significant_stress";
              const isMid = state === "mild_stress";
              const stateColor = isHigh ? "text-red-400" : isMid ? "text-amber-400" : "text-[#2E7D32]";
              const dotColor = isHigh ? "bg-red-400" : isMid ? "bg-amber-400" : "bg-[#2E7D32]";
              const stateLabel = state.replace(/_/g, " ").split(" ").map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

              const hasTwo = coercion.length > 0 && allStress.length > 0;

              return (
                <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <div className={`w-2 h-2 rounded-full ${dotColor}`} />
                    <p className="text-sm font-semibold">Cognitive state</p>
                  </div>

                  <div className="text-center mb-5">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Detected State</p>
                    <p className={`text-lg font-bold ${stateColor}`}>{stateLabel}</p>
                    <p className="text-xs text-slate-600 mt-0.5">Confidence: {(confidence * 100).toFixed(0)}%</p>
                  </div>

                  <div className={`grid gap-3 ${hasTwo ? "grid-cols-2" : "grid-cols-1"}`}>
                    {coercion.length > 0 && (
                      <div className="bg-[#0A0A15] border border-[#1E1E35] rounded-xl p-3.5">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2.5">Coercion Signals</p>
                        <div className="space-y-2">
                          {coercion.map((signal: string, i: number) => (
                            <div key={i} className="flex items-baseline gap-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-red-400 shrink-0 relative top-[-1px]" />
                              <span className="text-sm text-slate-300 leading-relaxed">{signal}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {allStress.length > 0 && (
                      <div className="bg-[#0A0A15] border border-[#1E1E35] rounded-xl p-3.5">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2.5">Stress Signals</p>
                        <div className="space-y-2">
                          {allStress.map((signal: string, i: number) => (
                            <div key={i} className="flex items-baseline gap-2">
                              <div className={`w-1.5 h-1.5 rounded-full shrink-0 relative top-[-1px] ${i < 2 ? "bg-amber-400" : "bg-blue-400"}`} />
                              <span className="text-sm text-slate-300 leading-relaxed">{signal}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}

            {/* Fraud Type */}
            {meta.fraud_type_assessment && (() => {
              const entries = Object.entries(meta.fraud_type_assessment) as [string, number][];
              const sorted = [...entries].sort((a, b) => b[1] - a[1]);

              function fraudBarColor(type: string, prob: number): string {
                if (type === "legitimate") {
                  return prob >= 0.5 ? "#2E7D32" : "#4ade80";
                }
                if (prob >= 0.6) return "#f87171";
                if (prob >= 0.3) return "#fbbf24";
                if (prob >= 0.1) return "#3b82f6";
                return "#2E7D32";
              }

              function fraudTextColor(type: string, prob: number): string {
                if (type === "legitimate") return "text-[#2E7D32]";
                if (prob >= 0.6) return "text-red-400";
                if (prob >= 0.3) return "text-amber-400";
                if (prob >= 0.1) return "text-blue-400";
                return "text-[#2E7D32]";
              }

              return (
                <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl p-5">
                  <div className="flex items-center gap-2 mb-5">
                    <div className="w-2 h-2 rounded-full bg-blue-400" />
                    <p className="text-sm font-semibold">Fraud type</p>
                  </div>
                  <div className="space-y-5">
                    {sorted.map(([type, prob]) => {
                      const pct = Math.round(prob * 100);
                      const color = fraudBarColor(type, prob);
                      const textClr = fraudTextColor(type, prob);
                      return (
                        <div key={type}>
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="text-sm font-medium capitalize">
                              {type.replace(/_/g, " ")}
                            </span>
                            <span className={`text-sm font-bold font-mono ${textClr}`}>
                              {pct}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-[#1E1E35] rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-700"
                              style={{ width: `${pct}%`, backgroundColor: color }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Recommended Actions */}
                  {meta.recommended_actions && meta.recommended_actions.length > 0 && (
                    <>
                      <div className="border-t border-[#1E1E35] my-5" />
                      <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">
                        Recommended Actions
                      </p>
                      <div className="space-y-2">
                        {meta.recommended_actions.map((action: string, i: number) => {
                          const actionColors = [
                            "text-red-400",
                            "text-blue-400",
                            "text-amber-400",
                            "text-slate-400",
                          ];
                          const dotColors = [
                            "bg-red-400",
                            "bg-blue-400",
                            "bg-amber-400",
                            "bg-slate-500",
                          ];
                          return (
                            <div key={i} className="flex items-center gap-2.5">
                              <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColors[i] || dotColors[3]}`} />
                              <span className={`text-sm font-mono ${actionColors[i] || actionColors[3]}`}>
                                {action}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Right: AI Chat */}
          <div className="lg:col-span-1 self-start sticky top-8">
          <div className="bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl flex flex-col h-[480px]">
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
                  className="bg-[#2E7D32] hover:bg-[#256d29] disabled:opacity-30 rounded-xl px-5 py-2.5 text-sm font-medium transition"
                >
                  Ask
                </button>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
}
