const API_BASE = "http://localhost:8000";

export async function login(
  userId: string,
  password: string
): Promise<{ success: boolean; name: string }> {
  const validUsers: Record<string, { password: string; name: string }> = {
    "mertali-tercan": { password: "mertali-tercan-1", name: "Mertali" },
    "ediz-uysal": { password: "ediz-uysal-1", name: "Ediz" },
    "deniz-coban": { password: "deniz-coban-1", name: "Deniz" },
  };

  const user = validUsers[userId];
  if (user && user.password === password) {
    return { success: true, name: user.name };
  }
  return { success: false, name: "" };
}

export async function submitTransaction(payload: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/transactions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function submitSessionTelemetry(payload: any): Promise<any> {
  // Session telemetry is logged locally for now — no backend endpoint needed.
  // The actual fraud analysis happens via demo scenarios or send money.
  console.log("[telemetry] session ended", payload.session_id);
  return null;
}

export async function triggerDemoScenario(
  scenarioName: string
): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/demo/scenario/${scenarioName}`,
    { method: "POST" }
  );
  return res.json();
}
