import { getSessionId } from "./session";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const sessionId = getSessionId();
  const headers = new Headers(options.headers || {});
  
  if (sessionId) {
    headers.set("x-session-id", sessionId);
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await res.json();
  if (!res.ok) {
    // throwing an object here, probably terrible practice but shrug
    throw { status: res.status, data };
  }
  return data;
}

export const api = {
  getRules: () => fetchApi("/"),
  startSession: () => fetchApi("/start"),
  getStatus: () => fetchApi("/status"),
  getRoomClue: (roomId: string) => fetchApi(`/room/${roomId}`),
  submitAnswer: (roomId: string, answer: string) => 
    fetchApi(`/room/${roomId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer })
    })
};
