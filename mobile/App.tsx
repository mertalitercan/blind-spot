import React, { useState, useRef, useCallback } from "react";
import { StatusBar } from "expo-status-bar";
import LoginScreen from "./screens/LoginScreen";
import HomeScreen from "./screens/HomeScreen";
import { TelemetryTracker } from "./lib/telemetry";
import { submitSessionTelemetry } from "./lib/api";

export default function App() {
  const [user, setUser] = useState<{
    userId: string;
    name: string;
  } | null>(null);
  const trackerRef = useRef<TelemetryTracker | null>(null);

  const handleLogin = useCallback((userId: string, name: string) => {
    const tracker = new TelemetryTracker(userId);
    tracker.startSession();
    tracker.recordNavigation("home");
    trackerRef.current = tracker;
    setUser({ userId, name });
  }, []);

  const handleLogout = useCallback(async () => {
    if (trackerRef.current) {
      const snapshot = trackerRef.current.getSnapshot();
      trackerRef.current.destroy();
      trackerRef.current = null;
      submitSessionTelemetry(snapshot).catch(() => {});
    }
    setUser(null);
  }, []);

  return (
    <>
      <StatusBar style="light" />
      {user ? (
        <HomeScreen
          user={user}
          tracker={trackerRef.current}
          onLogout={handleLogout}
        />
      ) : (
        <LoginScreen onLogin={handleLogin} />
      )}
    </>
  );
}
