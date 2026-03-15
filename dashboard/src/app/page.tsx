"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    setTimeout(() => {
      if (username === "admin" && password === "admin") {
        sessionStorage.setItem("authed", "true");
        router.push("/dashboard");
      } else {
        setError("Invalid credentials");
        setLoading(false);
      }
    }, 600);
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-[#2E7D32]/4 rounded-full blur-[150px]" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#2E7D32]/3 rounded-full blur-[120px]" />
      <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-blue-500/2 rounded-full blur-[100px]" />

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div className="w-full max-w-md relative z-10 px-6">
        {/* Logo section */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-bounce" />
            <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:150ms]" />
            <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-bounce [animation-delay:300ms]" />
          </div>
          <h1 className="text-4xl font-light tracking-tight">
            Blind<span className="font-bold">Spot</span>
          </h1>
          <p className="text-sm text-slate-500 mt-3 tracking-[0.25em] uppercase">
            Fraud Detection System
          </p>
        </div>

        {/* Login card */}
        <div className="bg-[#0A0A15]/80 backdrop-blur-xl border border-[#1E1E35] rounded-2xl p-8">
          <div className="mb-6">
            <h2 className="text-lg font-semibold">Sign in</h2>
            <p className="text-sm text-slate-500 mt-1">
              Access the fraud monitoring dashboard
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs text-slate-500 uppercase tracking-wider mb-1.5 block">
                Username
              </label>
              <div className="relative">
                <svg
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#050510] border border-[#1E1E35] rounded-xl pl-11 pr-5 py-3 text-white outline-none focus:border-[#2E7D32]/50 focus:ring-1 focus:ring-[#2E7D32]/20 transition placeholder:text-slate-700"
                  placeholder="Enter username"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-500 uppercase tracking-wider mb-1.5 block">
                Password
              </label>
              <div className="relative">
                <svg
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#050510] border border-[#1E1E35] rounded-xl pl-11 pr-5 py-3 text-white outline-none focus:border-[#2E7D32]/50 focus:ring-1 focus:ring-[#2E7D32]/20 transition placeholder:text-slate-700"
                  placeholder="Enter password"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
                <svg
                  className="w-4 h-4 text-red-400 shrink-0"
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
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#2E7D32] hover:bg-[#256d29] disabled:opacity-70 rounded-xl py-3.5 font-semibold transition text-white flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>
                  <svg
                    className="w-4 h-4 animate-spin"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="3"
                      className="opacity-25"
                    />
                    <path
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      className="opacity-75"
                    />
                  </svg>
                  Authenticating...
                </>
              ) : (
                <>
                  Access Dashboard
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
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    />
                  </svg>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-center gap-3 mt-8">
          <div className="w-2 h-2 rounded-full bg-[#2E7D32]/40" />
          <p className="text-slate-600 text-xs tracking-wide">
            Authorized personnel only
          </p>
        </div>
      </div>
    </div>
  );
}
