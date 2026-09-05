const AI_SERVICE_URL = process.env.ML_SERVICE_URL || "http://127.0.0.1:8000";

async function requestML(path, { method = "GET", query = {}, body } = {}) {
  const url = new URL(path, AI_SERVICE_URL);
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null) url.searchParams.set(key, String(value));
  });

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : { detail: await response.text() };
    return { status: response.status, data };
  } finally {
    clearTimeout(timeout);
  }
}

module.exports = { requestML };
