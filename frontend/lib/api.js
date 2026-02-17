const RAW_BASE = (process.env.NEXT_PUBLIC_API_URL || "").trim();

function runtimeBase() {
  if (!RAW_BASE) return "";

  // Codespaces safety: if build-time base is localhost but app is opened on github.dev,
  // use relative /api proxy instead of broken browser localhost target.
  if (typeof window !== "undefined") {
    const host = window.location.hostname || "";
    const remoteHost = host && host !== "localhost" && host !== "127.0.0.1";
    if (remoteHost && RAW_BASE.includes("localhost")) {
      return "";
    }
  }

  return RAW_BASE.replace(/\/$/, "");
}

function buildUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const base = runtimeBase();
  if (!base) return normalizedPath;
  return `${base}${normalizedPath}`;
}

export async function apiGet(path) {
  const response = await fetch(buildUrl(path), {
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
  const response = await fetch(buildUrl(path), {
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
  const response = await fetch(buildUrl(path), {
    method: "DELETE",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

export function apiBase() {
  return runtimeBase();
}
