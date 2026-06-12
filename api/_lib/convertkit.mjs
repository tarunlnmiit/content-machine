// Kit (ConvertKit) v4 client. Verified against developers.kit.com.
// Auth: custom header X-Kit-Api-Key (NOT Authorization: Bearer — that's OAuth).
const BASE_URL = "https://api.kit.com/v4";

const tagIdCache = new Map(); // name -> id, per cold start

function apiKey() {
  const k = process.env.CONVERTKIT_API_KEY;
  if (!k) throw new Error("CONVERTKIT_API_KEY is not set");
  return k;
}

async function kit(path, { method = "GET", body } = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "X-Kit-Api-Key": apiKey(),
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Kit API ${method} ${path} -> ${res.status}: ${text.slice(0, 300)}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// Returns true if the email already exists in the Kit database.
export async function subscriberExists(email) {
  const data = await kit(`/subscribers?email_address=${encodeURIComponent(email)}`);
  return Array.isArray(data?.subscribers) && data.subscribers.length > 0;
}

// POST /subscribers is an upsert — call subscriberExists() first to classify.
export async function upsertSubscriber(email) {
  return kit(`/subscribers`, { method: "POST", body: { email_address: email } });
}

export async function resolveTagId(name) {
  if (tagIdCache.has(name)) return tagIdCache.get(name);
  const data = await kit(`/tags`);
  for (const t of data?.tags ?? []) tagIdCache.set(t.name, t.id);
  if (!tagIdCache.has(name)) {
    const created = await kit(`/tags`, { method: "POST", body: { name } });
    tagIdCache.set(name, created?.tag?.id);
  }
  return tagIdCache.get(name);
}

// POST /subscribers/{email}/tags — tag by email, no subscriber id needed.
export async function tagSubscriber(email, tagId) {
  return kit(`/subscribers/${encodeURIComponent(email)}/tags`, {
    method: "POST",
    body: { tag_id: tagId },
  });
}

// Full flow: classify, upsert, tag. Returns "first_time" | "returning".
export async function captureAndTag(email) {
  const exists = await subscriberExists(email);
  await upsertSubscriber(email); // upsert is safe whether new or returning
  const tagName = exists ? "worksheet_repeat_visitor" : "first_time_worksheet";
  const tagId = await resolveTagId(tagName);
  if (tagId) await tagSubscriber(email, tagId);
  return exists ? "returning" : "first_time";
}
