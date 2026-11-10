// Gọi API server local + tiện ích chung
export const $ = (s, r = document) => r.querySelector(s);
export const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const OLD_SERVER = "Server đang chạy bản cũ – hãy tắt và mở lại app (nhấp đúp “Mo DT-RnD-Lab.command”) để nạp bản mới.";

export async function get(path) {
  const r = await fetch(path);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error === "not_found" && path.startsWith("/api/") ? OLD_SERVER : (j.error || r.statusText));
  return j;
}

export async function post(path, body, raw = false) {
  const r = await fetch(path, {
    method: "POST",
    headers: raw ? {} : { "Content-Type": "application/json" },
    body: raw ? body : JSON.stringify(body || {}),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error === "not_found" ? OLD_SERVER : (j.error || r.statusText));
  return j;
}

export function toast(msg, err = false) {
  const t = document.createElement("div");
  t.className = "toast" + (err ? " err" : "");
  t.textContent = msg;
  $("#toast-root").appendChild(t);
  setTimeout(() => t.remove(), err ? 6000 : 3200);
}

// Chờ job nền (hỏi Qwen, vòng tuần, nạp tài liệu) xong; onLog nhận log mới
export async function waitJob(id, onLog) {
  for (;;) {
    const j = await get(`/api/job?id=${id}`);
    if (onLog) onLog(j.log || []);
    if (j.state !== "running") {
      if (j.state === "error") throw new Error(j.result);
      return j.result;
    }
    await new Promise(r => setTimeout(r, 1500));
  }
}

export function fmtDate(iso) {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}
