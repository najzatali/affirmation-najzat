const SESSION_KEY = "studio_session_v1";
const HISTORY_KEY = "studio_history_v1";

function safeParse(raw, fallback) {
  try {
    return JSON.parse(raw);
  } catch (_e) {
    return fallback;
  }
}

export function readSession() {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  return safeParse(raw, null);
}

export function saveSession(data) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(data || null));
}

export function clearSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(SESSION_KEY);
}

export function readHistory() {
  if (typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(HISTORY_KEY);
  if (!raw) return [];
  const parsed = safeParse(raw, []);
  return Array.isArray(parsed) ? parsed : [];
}

export function pushHistory(item) {
  if (typeof window === "undefined") return;
  const current = readHistory();
  const next = [item, ...current].slice(0, 50);
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}

export function patchHistory(predicate, patch) {
  if (typeof window === "undefined") return;
  const current = readHistory();
  const next = current.map((item) => {
    if (!predicate(item)) return item;
    return { ...item, ...patch };
  });
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}
