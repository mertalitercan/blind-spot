import { AppState, AppStateStatus } from "react-native";

export interface KeystrokeEvent {
  field: string;
  timestamp_ms: number;
  char_delta: number; // +1 = typed, -1 = backspace, >1 = paste
}

export interface TouchEvent {
  x: number;
  y: number;
  timestamp_ms: number;
  event_type: "press" | "release" | "move";
}

export interface NavigationEntry {
  screen_name: string;
  timestamp_ms: number;
  duration_ms: number;
}

export interface DeadTimePeriod {
  start_ms: number;
  end_ms: number;
  duration_ms: number;
}

export interface AppSwitch {
  timestamp_ms: number;
  duration_away_ms: number;
}

export interface TelemetrySnapshot {
  session_id: string;
  user_id: string;
  session_start: string;
  session_end: string;
  session_duration_ms: number;
  keystroke_events: KeystrokeEvent[];
  touch_events: TouchEvent[];
  navigation_path: NavigationEntry[];
  dead_time_periods: DeadTimePeriod[];
  app_switches: AppSwitch[];
  typing_speed_wpm: number;
  error_rate: number;
  typing_rhythm_signature: number[];
  segmented_typing_detected: boolean;
  paste_detected: boolean;
  paste_field: string;
  confirm_button_hesitation_ms: number;
  confirm_attempts: number;
  total_dead_time_ms: number;
  avg_touch_pressure: number;
  avg_touch_radius: number;
  hand_dominance: string;
  navigation_directness_score: number;
  screen_familiarity_score: number;
}

const DEAD_TIME_THRESHOLD_MS = 5000;
const SEGMENTED_TYPING_PAUSE_MS = 3000;

export class TelemetryTracker {
  private sessionId: string;
  private userId: string;
  private startTime: number = 0;
  private keystrokeEvents: KeystrokeEvent[] = [];
  private touchEvents: TouchEvent[] = [];
  private navigationPath: NavigationEntry[] = [];
  private deadTimePeriods: DeadTimePeriod[] = [];
  private appSwitches: AppSwitch[] = [];
  private lastInteractionTime: number = 0;
  private lastKeystrokeTime: number = 0;
  private interKeyIntervals: number[] = [];
  private totalCharsTyped: number = 0;
  private totalBackspaces: number = 0;
  private pasteDetected: boolean = false;
  private pasteField: string = "";
  private confirmHesitationStart: number = 0;
  private confirmHesitationMs: number = 0;
  private confirmAttempts: number = 0;
  private currentScreen: string = "";
  private screenEntryTime: number = 0;
  private appBackgroundTime: number = 0;
  private appStateSubscription: any = null;

  constructor(userId: string) {
    this.sessionId = this.generateId();
    this.userId = userId;
  }

  private generateId(): string {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
      /[xy]/g,
      (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }
    );
  }

  startSession(): void {
    this.startTime = Date.now();
    this.lastInteractionTime = this.startTime;

    this.appStateSubscription = AppState.addEventListener(
      "change",
      this.handleAppStateChange
    );
  }

  private handleAppStateChange = (nextState: AppStateStatus): void => {
    const now = Date.now();
    if (nextState === "background" || nextState === "inactive") {
      this.appBackgroundTime = now;
    } else if (nextState === "active" && this.appBackgroundTime > 0) {
      const awayMs = now - this.appBackgroundTime;
      this.appSwitches.push({
        timestamp_ms: this.appBackgroundTime - this.startTime,
        duration_away_ms: awayMs,
      });
      this.appBackgroundTime = 0;
    }
  };

  recordTouch(x: number, y: number, type: "press" | "release" | "move"): void {
    const now = Date.now();
    this.checkDeadTime(now);
    this.lastInteractionTime = now;

    this.touchEvents.push({
      x,
      y,
      timestamp_ms: now - this.startTime,
      event_type: type,
    });
  }

  recordTextChange(field: string, newText: string, oldText: string): void {
    const now = Date.now();
    this.checkDeadTime(now);
    this.lastInteractionTime = now;

    const delta = newText.length - oldText.length;

    // Paste detection: large text change at once
    if (delta > 3) {
      this.pasteDetected = true;
      this.pasteField = field;
    }

    if (delta > 0) {
      this.totalCharsTyped += delta;
    } else if (delta < 0) {
      this.totalBackspaces += Math.abs(delta);
    }

    // Inter-key interval
    if (this.lastKeystrokeTime > 0) {
      const interval = now - this.lastKeystrokeTime;
      this.interKeyIntervals.push(interval);
    }
    this.lastKeystrokeTime = now;

    this.keystrokeEvents.push({
      field,
      timestamp_ms: now - this.startTime,
      char_delta: delta,
    });
  }

  recordNavigation(screenName: string): void {
    const now = Date.now();

    // Close previous screen entry
    if (this.currentScreen && this.screenEntryTime > 0) {
      this.navigationPath.push({
        screen_name: this.currentScreen,
        timestamp_ms: this.screenEntryTime - this.startTime,
        duration_ms: now - this.screenEntryTime,
      });
    }

    this.currentScreen = screenName;
    this.screenEntryTime = now;
  }

  recordConfirmApproach(): void {
    this.confirmHesitationStart = Date.now();
    this.confirmAttempts++;
  }

  recordConfirmPress(): void {
    if (this.confirmHesitationStart > 0) {
      this.confirmHesitationMs = Date.now() - this.confirmHesitationStart;
    }
  }

  private checkDeadTime(now: number): void {
    const gap = now - this.lastInteractionTime;
    if (gap > DEAD_TIME_THRESHOLD_MS && this.lastInteractionTime > 0) {
      this.deadTimePeriods.push({
        start_ms: this.lastInteractionTime - this.startTime,
        end_ms: now - this.startTime,
        duration_ms: gap,
      });
    }
  }

  getSnapshot(): TelemetrySnapshot {
    const now = Date.now();
    const sessionDuration = now - this.startTime;

    // Close current screen
    if (this.currentScreen && this.screenEntryTime > 0) {
      this.navigationPath.push({
        screen_name: this.currentScreen,
        timestamp_ms: this.screenEntryTime - this.startTime,
        duration_ms: now - this.screenEntryTime,
      });
    }

    // Compute typing speed (chars per minute → WPM assuming 5 chars/word)
    const typingDurationMs =
      this.keystrokeEvents.length > 1
        ? this.keystrokeEvents[this.keystrokeEvents.length - 1].timestamp_ms -
          this.keystrokeEvents[0].timestamp_ms
        : 1;
    const typingSpeedWpm =
      typingDurationMs > 0
        ? (this.totalCharsTyped / 5 / (typingDurationMs / 60000))
        : 0;

    // Error rate
    const totalKeystrokes = this.totalCharsTyped + this.totalBackspaces;
    const errorRate =
      totalKeystrokes > 0 ? this.totalBackspaces / totalKeystrokes : 0;

    // Segmented typing detection
    const segmentedTyping = this.interKeyIntervals.some(
      (i) => i > SEGMENTED_TYPING_PAUSE_MS
    );

    // Typing rhythm signature (first 10 inter-key intervals)
    const rhythmSig = this.interKeyIntervals.slice(0, 10);

    // Total dead time
    const totalDeadTime = this.deadTimePeriods.reduce(
      (sum, p) => sum + p.duration_ms,
      0
    );

    // Navigation directness (ratio of screens visited to minimum needed)
    const uniqueScreens = new Set(this.navigationPath.map((n) => n.screen_name)).size;
    const directness = uniqueScreens > 0 ? Math.min(1, 2 / uniqueScreens) : 1;

    // Infer hand dominance from touch x coordinates
    const touchXes = this.touchEvents.filter((t) => t.event_type === "press").map((t) => t.x);
    const avgX = touchXes.length > 0 ? touchXes.reduce((a, b) => a + b, 0) / touchXes.length : 200;
    const handDominance = avgX > 200 ? "right" : "left";

    return {
      session_id: this.sessionId,
      user_id: this.userId,
      session_start: new Date(this.startTime).toISOString(),
      session_end: new Date(now).toISOString(),
      session_duration_ms: sessionDuration,
      keystroke_events: this.keystrokeEvents,
      touch_events: this.touchEvents,
      navigation_path: this.navigationPath,
      dead_time_periods: this.deadTimePeriods,
      app_switches: this.appSwitches,
      typing_speed_wpm: Math.round(typingSpeedWpm * 10) / 10,
      error_rate: Math.round(errorRate * 1000) / 1000,
      typing_rhythm_signature: rhythmSig,
      segmented_typing_detected: segmentedTyping,
      paste_detected: this.pasteDetected,
      paste_field: this.pasteField,
      confirm_button_hesitation_ms: this.confirmHesitationMs,
      confirm_attempts: this.confirmAttempts,
      total_dead_time_ms: totalDeadTime,
      avg_touch_pressure: 0.45, // RN doesn't expose pressure; use default
      avg_touch_radius: 12.0,
      hand_dominance: handDominance,
      navigation_directness_score: Math.round(directness * 1000) / 1000,
      screen_familiarity_score: Math.min(1, Math.max(0, 1 - errorRate * 2)),
    };
  }

  destroy(): void {
    if (this.appStateSubscription) {
      this.appStateSubscription.remove();
    }
  }
}
