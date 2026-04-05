export const SESSION_KEY = "escape_session_id";

export function getSessionId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(SESSION_KEY);
}

export function setSessionId(id: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(SESSION_KEY, id);
  }
}

export function clearSessionId() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(SESSION_KEY);
  }
}
