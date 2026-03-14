"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (username === "admin" && password === "admin") {
      sessionStorage.setItem("authed", "true");
      router.push("/dashboard");
    } else {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Subtle gradient orb */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[120px]" />

      <div className="w-full max-w-sm relative z-10">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="w-3 h-3 rounded-full bg-indigo-400 animate-pulse" />
            <div className="w-3 h-3 rounded-full bg-indigo-400/60 animate-pulse [animation-delay:150ms]" />
            <div className="w-3 h-3 rounded-full bg-indigo-400/30 animate-pulse [animation-delay:300ms]" />
          </div>
          <h1 className="text-3xl font-light tracking-tight">
            Blind<span className="font-bold">Spot</span>
          </h1>
          <p className="text-sm text-slate-500 mt-2 tracking-wide">
            FRAUD DETECTION SYSTEM
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#0F0F1A] border border-[#1E1E35] rounded-xl px-5 py-3.5 text-white outline-none focus:border-indigo-500/50 transition placeholder:text-slate-600"
              placeholder="Username"
            />
          </div>
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#0F0F1A] border border-[#1E1E35] rounded-xl px-5 py-3.5 text-white outline-none focus:border-indigo-500/50 transition placeholder:text-slate-600"
              placeholder="Password"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full bg-indigo-500 hover:bg-indigo-600 rounded-xl py-3.5 font-semibold transition text-white"
          >
            Access Dashboard
          </button>
        </form>

        <p className="text-center text-slate-600 text-xs mt-8">
          Authorized personnel only
        </p>
      </div>
    </div>
  );
}
