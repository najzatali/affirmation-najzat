const API = process.env.NEXT_PUBLIC_API_URL || "";

function ensureApi() {
  if (!API) {
    throw new Error("NEXT_PUBLIC_API_URL is empty");
  }
  return API;
}

export async function apiGet(path) {
  const base = ensureApi();
  const response = await fetch(`${base}${path}`, {
    method: "GET",
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

export async function apiPost(path, payload) {
  const base = ensureApi();
  const response = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload || {}),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

export async function apiDelete(path) {
  const base = ensureApi();
  const response = await fetch(`${base}${path}`, {
    method: "DELETE",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

export function apiBase() {
  return API;
}
