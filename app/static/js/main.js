// VTI R&D Lab — router các tab (cùng kiểu EnglishCoach) + các màn hình. Phòng R&D đa module (DT là module đầu tiên).
import { $, esc, get, post, toast, waitJob, fmtDate } from "./api.js";
import { drawOffice, avatar } from "./office.js";

const view = () => $("#view");
let TEAM = [];
let STATUS = null;
let MODS = [];
let askAgent = null; // agent đang chọn ở tab Hỏi
let askModule = ""; // module đang chọn ở tab Hỏi ("" = cả phòng)
const STATUS_PILL = { active: "ok", standby: "warn", paused: "" };

function page(html) {
  view().innerHTML = `<div class="page">${html}</div>`;
}

function greetWord() {
  const h = new Date().getHours();
  return h < 11 ? "Chào buổi sáng" : h < 14 ? "Chào buổi trưa" : h < 18 ? "Chào buổi chiều" : "Chào buổi tối";
}

async function refreshChips() {
  try {
    STATUS = await get("/api/status");
    const m = STATUS.modules || { active: 0, total: 0 };
    $("#phase-chip").textContent = `🧩 ${m.active}/${m.total} module đang nghiên cứu`;
    const eng = STATUS.ollama_ok ? STATUS.chat_model : "Ollama chưa chạy";
    $("#engine-chip").textContent = `🧠 ${eng}${STATUS.cloud.enabled ? " + ☁️" : ""}`;
    $("#job-chip").hidden = !STATUS.jobs_running;
    $("#job-chip").textContent = `⏳ ${STATUS.jobs_running} việc đang chạy`;
  } catch (e) { /* server đang khởi động */ }
}

// ------------------------------------------------------------ 🏠 Hôm nay
function modCard(m, compact = false) {
  const p = m.phase;
  return `<div class="card click mod-card" data-m="${esc(m.id)}">
    <div class="card-head"><h3>${esc(m.icon || "🧪")} ${esc(m.name)}</h3><span class="pill ${STATUS_PILL[m.status] || ""}">${esc(m.status_vi)}</span></div>
    <div class="small"><b>${esc(p.code)} · ${esc(p.name)}</b> <span class="muted">(${fmtDate(p.start)} → ${fmtDate(p.end)})</span></div>
    <div class="bar" style="margin:8px 0"><i style="width:${Math.round(p.pct * 100)}%"></i></div>
    ${compact ? "" : `<p class="small muted" style="margin:6px 0">${esc((m.goal || "").slice(0, 170))}${(m.goal || "").length > 170 ? "…" : ""}</p>`}
    <div class="small muted">👥 ${m.members.length} chuyên viên riêng · 📚 ${m.docs} tài liệu</div></div>`;
}

async function today() {
  page(`<p class="muted">Đang tải…</p>`);
  const [st, reports, mods] = await Promise.all([get("/api/status"), get("/api/reports"), get("/api/modules")]);
  STATUS = st; MODS = mods;
  const active = mods.filter(m => m.status === "active");
  const cyc = reports.find(r => r.path.includes("/cycles/"));
  const last = cyc || reports[0];
  const office = TEAM.filter(p => p.key === "director" || p.module === "shared" || active.some(m => m.id === p.module));
  page(`
    <div class="card hero">
      <h1 class="greet">${greetWord()} anh Khương đẹp trai 👋</h1>
      <p>Phòng R&amp;D Năng lượng &amp; Công nghệ có <b>${mods.length} module</b>, trong đó <b>${active.length} đang nghiên cứu</b>: ${active.map(m => esc(m.icon + " " + m.name)).join(", ") || "—"}.</p>
      <p class="small">Mỗi 3 ngày Trưởng phòng tự chạy một chu kỳ cho các module đang hoạt động và gửi anh <b>Báo cáo 3 ngày</b> – chỉ gồm những gì mới nghiên cứu/bổ sung.</p>
      <div class="row" style="margin-top:12px">
        <button class="btn" id="go-ask">🤖 Hỏi phòng R&amp;D</button>
        <button class="btn" id="go-week">🗓 Chạy chu kỳ ngay</button>
        <button class="btn" id="go-mod">➕ Mở module mới</button>
        <button class="btn" id="go-tree">🌳 Sơ đồ cây</button>
      </div>
    </div>

    <h2 class="section-h">🧩 Các module nghiên cứu</h2>
    <div class="grid g3">${mods.map(m => modCard(m)).join("")}</div>

    <div class="card scene-wrap" style="margin-top:16px"><div id="office"></div></div>
    <p class="small muted" style="margin:6px 4px">Nhân sự các module đang hoạt động + khối dùng chung (🤝). Bấm vào một người để hỏi trực tiếp.</p>

    <div class="grid g4" style="margin-top:12px">
      <div class="card stat"><div class="stat-value">${st.reports}</div><div class="stat-label">Báo cáo đã có</div></div>
      <div class="card stat"><div class="stat-value">${st.kb.documents}</div><div class="stat-label">Tài liệu trong kho (${st.kb.chunks} đoạn)</div></div>
      <div class="card stat"><div class="stat-value">${st.ollama_ok ? "✅" : "⚠️"}</div><div class="stat-label">${st.ollama_ok ? "Qwen local sẵn sàng" : "Ollama chưa chạy"}</div></div>
      <div class="card stat"><div class="stat-value">${TEAM.length}</div><div class="stat-label">Nhân sự AI (${TEAM.filter(p => p.module === "shared").length} dùng chung)</div></div>
    </div>

    <h2 class="section-h">🎯 Cơ hội hôm nay từ bản tin năng lượng</h2>
    <div id="dash-news" class="list"><div class="card muted small">Đang tải…</div></div>

    <h2 class="section-h">📑 ${cyc ? "Báo cáo 3 ngày mới nhất" : "Báo cáo mới nhất"}</h2>
    ${last ? `<div class="card click" id="last-rep"><div class="card-head"><h3>${esc(last.title)}</h3><div class="row"><span class="pill">${esc(last.week)}</span><a class="btn" id="last-docx" href="/api/report.docx?path=${encodeURIComponent(last.path)}" download>📄 Word</a></div></div>
      <div class="small muted">Cập nhật ${esc(last.mtime)} · bấm để đọc</div></div>` : `<div class="card muted">Chưa có báo cáo. Bấm “Chạy chu kỳ ngay”.</div>`}
  `);
  get("/api/news").then(r => {
    const box = $("#dash-news");
    if (!box) return;
    const d = r.digest;
    if (!d || !d.items.length) { box.innerHTML = '<div class="card small muted">Chưa có tin – vào tab 📰 Tin tức &amp; Cơ hội để cập nhật.</div>'; return; }
    const top = d.items.filter(x => x.is_opportunity).slice(0, 4);
    box.innerHTML = (top.length ? top : d.items.slice(0, 4)).map(x => `<a class="list-item" href="${esc(x.link)}" target="_blank" rel="noopener" style="text-decoration:none;color:var(--ink)">
      <div><b>${esc(x.title)}</b><div class="small muted">${esc(x.publisher)} · ${esc(x.category_vi)}</div></div><span class="pill">${x.score}</span></a>`).join("")
      + `<a class="small" href="#news">Xem đủ ${d.items.length} tin ngày ${d.date} →</a>`;
  }).catch(() => {});
  drawOffice($("#office"), office, pk => { askAgent = pk.key === "director" ? null : pk.key; askModule = pk.module && !["shared", "director"].includes(pk.module) ? pk.module : ""; location.hash = "ask"; });
  view().querySelectorAll(".mod-card").forEach(c => c.onclick = () => (location.hash = "modules:" + c.dataset.m));
  $("#go-ask").onclick = () => (location.hash = "ask");
  $("#go-tree").onclick = () => (location.hash = "tree");
  $("#go-mod").onclick = () => (location.hash = "modules:new");
  $("#go-week").onclick = () => runCycle();
  if (last) {
    $("#last-rep").onclick = () => (location.hash = "reports:" + encodeURIComponent(last.path));
    $("#last-docx").onclick = e => e.stopPropagation();
  }
}

async function runCycle(modules = []) {
  const focus = prompt("Trọng tâm chu kỳ này (để trống = theo lộ trình từng module):", "") ?? null;
  if (focus === null) return;
  try {
    const { job } = await post("/api/cycle", { focus, modules });
    toast("Đã giao việc cho các module. Qwen local có thể mất 15–60 phút…");
    refreshChips();
    const res = await waitJob(job);
    toast("✅ Xong báo cáo: " + res.path);
    location.hash = "reports:" + encodeURIComponent(res.path);
  } catch (e) { toast("Lỗi chu kỳ nghiên cứu: " + e.message, true); }
  refreshChips();
}

// ------------------------------------------------------------ 🧩 Module
const ICONS = ["🧪", "⚡", "🛰", "🌬", "☀️", "🏭", "🔌", "💧", "🤖", "🛡", "📈", "🧠"];

async function modulesView(arg) {
  MODS = await get("/api/modules");
  if (arg === "new") return moduleForm();
  const m = MODS.find(x => x.id === arg);
  if (!m) {
    page(`<div class="card hero"><div class="card-head"><h3>🧩 Các module nghiên cứu</h3><button class="btn btn-primary" id="new-mod">➕ Mở module mới</button></div>
      <p class="small">Mỗi module là một chủ đề nghiên cứu có mục tiêu, lộ trình, nhóm chuyên viên riêng và thư mục tài liệu riêng; dùng chung Trưởng phòng và khối chuyên viên 🤝 (tiêu chuẩn, dữ liệu &amp; AI, OT/an ninh mạng, benchmark, thị trường VN). Module <b>Đang nghiên cứu</b> được đưa vào chu kỳ báo cáo 3 ngày; module <b>Chờ kích hoạt</b> đã có khung, chờ anh đưa nội dung.</p></div>
      <div class="grid g3" style="margin-top:16px">${MODS.map(x => modCard(x)).join("")}</div>`);
    $("#new-mod").onclick = () => (location.hash = "modules:new");
    view().querySelectorAll(".mod-card").forEach(c => c.onclick = () => (location.hash = "modules:" + c.dataset.m));
    return;
  }
  const people = TEAM.filter(p => p.module === m.id);
  const shared = TEAM.filter(p => (m.shared || []).includes(p.key));
  const today = new Date().toISOString().slice(0, 10);
  const li = a => (a || []).map(x => `<li>${esc(x)}</li>`).join("");
  page(`
    <div class="card hero">
      <div class="card-head"><h3 style="font-size:22px">${esc(m.icon)} ${esc(m.name)}</h3><span class="pill ${STATUS_PILL[m.status] || ""}">${esc(m.status_vi)}</span></div>
      <p>${esc(m.goal)}</p><p class="small"><b>Phạm vi:</b> ${esc(m.scope)}</p>
      <div class="row" style="margin-top:10px">
        <button class="btn" id="m-ask">🤖 Hỏi module này</button>
        <button class="btn" id="m-run">🗓 Chạy chu kỳ cho module</button>
        ${m.status === "active" ? `<button class="btn" data-st="paused">⏸ Tạm dừng</button>` : `<button class="btn btn-primary" data-st="active">▶️ Kích hoạt nghiên cứu</button>`}
        ${m.status !== "standby" ? `<button class="btn" data-st="standby">💤 Chuyển chờ</button>` : ""}
        <a class="btn" href="#library:${encodeURIComponent((m.library || [])[0] || "")}">📚 Tài liệu (${m.docs})</a>
      </div>
    </div>
    <h2 class="section-h">🧭 Lộ trình</h2>
    <div class="phases">${m.phase.all.map(x => `<div class="phase ${x.code === m.phase.code ? "now" : x.end < today ? "done" : ""}"><b>${esc(x.code)} · ${esc(x.name)}</b><span class="small muted">${fmtDate(x.start)} → ${fmtDate(x.end)}</span></div>`).join("")}</div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>❓ Câu hỏi nghiên cứu chính</h3><ul class="small">${li(m.questions)}</ul>
        ${m.keywords?.length ? `<div class="small muted">Từ khóa tra cứu: ${m.keywords.map(esc).join(", ")}</div>` : ""}
        <div class="small muted" style="margin-top:6px">Thư mục tài liệu: ${(m.library || []).map(x => `<code>library/${esc(x)}</code>`).join(", ")}</div></div>
      <div class="card"><h3>🤝 Mượn khối dùng chung</h3><div class="agent-picker">${shared.map(p => `<button data-k="${p.key}">${avatar(p, 24)} ${esc(p.name)} · ${esc(p.role)}</button>`).join("") || '<span class="muted small">—</span>'}</div></div>
    </div>
    <h2 class="section-h">👥 Chuyên viên riêng của module</h2>
    <div class="grid g2">${people.map(p => personCard(p)).join("")}</div>`);
  $("#m-ask").onclick = () => { askModule = m.id; askAgent = null; location.hash = "ask"; };
  $("#m-run").onclick = () => runCycle([m.id]);
  view().querySelectorAll("[data-st]").forEach(b => b.onclick = async () => {
    try { await post("/api/modules/status", { id: m.id, status: b.dataset.st }); toast("Đã cập nhật trạng thái module"); refreshChips(); modulesView(m.id); }
    catch (e) { toast(e.message, true); }
  });
  view().querySelectorAll("button[data-k]").forEach(b => b.onclick = () => { askAgent = b.dataset.k; askModule = m.id; location.hash = "ask"; });
}

function moduleForm() {
  const d0 = new Date().toISOString().slice(0, 10);
  page(`
    <div class="card">
      <div class="card-head"><h3>➕ Mở module nghiên cứu mới</h3><a class="btn" href="#modules">← Danh sách module</a></div>
      <p class="small muted">Anh điền nội dung, Trưởng phòng (Qwen) sẽ tự thiết kế 2–4 chuyên viên riêng, lộ trình giai đoạn, từ khóa tra cứu, tạo thư mục <code>library/m_&lt;module&gt;</code> và bài giới thiệu module trong Báo cáo. Nếu Ollama chưa chạy, app dùng khung mặc định để anh sửa sau.</p>
      <div class="form-grid">
        <label class="f">Tên module *<input id="f-name" placeholder="VD: Điện gió ngoài khơi"></label>
        <label class="f">Biểu tượng<select id="f-icon">${ICONS.map(i => `<option>${i}</option>`).join("")}</select></label>
        <label class="f">Trạng thái ban đầu<select id="f-status"><option value="active">Đang nghiên cứu</option><option value="standby">Chờ kích hoạt</option></select></label>
        <label class="f">Bắt đầu<input id="f-start" type="date" value="${d0}"></label>
        <label class="f">Hạn hoàn thành<input id="f-deadline" type="date"></label>
      </div>
      <label class="f">Mục tiêu nghiên cứu *<textarea id="f-goal" style="min-height:70px" placeholder="Muốn hiểu / làm được gì, để phục vụ việc gì của VTI"></textarea></label>
      <label class="f">Phạm vi (thiết bị, cấp điện áp, khách hàng…)<textarea id="f-scope" style="min-height:60px"></textarea></label>
      <label class="f">Câu hỏi nghiên cứu chính (mỗi dòng 1 câu)<textarea id="f-questions" style="min-height:80px"></textarea></label>
      <label class="f">Tiêu chuẩn / tài liệu / hãng cần bám (cách nhau dấu phẩy)<input id="f-refs" placeholder="VD: IEC 61400-25, CIGRE TB …, Vestas, Siemens Gamesa"></label>
      <div class="row" style="margin-top:12px"><button class="btn btn-primary" id="f-go">🚀 Mở module</button></div>
      <pre class="log" id="f-log" hidden></pre>
    </div>`);
  $("#f-go").onclick = async () => {
    const v = id => $("#" + id).value.trim();
    const body = { name: v("f-name"), icon: v("f-icon"), status: v("f-status"), start: v("f-start"), deadline: v("f-deadline"),
                   goal: v("f-goal"), scope: v("f-scope"), questions: v("f-questions"), references: v("f-refs") };
    if (!body.name || !body.goal) return toast("Cần nhập tên và mục tiêu module", true);
    const btn = $("#f-go"), log = $("#f-log");
    btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Đang thiết kế module…'; log.hidden = false;
    try {
      const { job } = await post("/api/modules", body);
      const r = await waitJob(job, l => { log.textContent = l.join("\n"); });
      TEAM = await get("/api/team");
      toast("✅ Đã mở module " + body.name);
      refreshChips();
      location.hash = "modules:" + r.id;
    } catch (e) { toast(e.message, true); btn.disabled = false; btn.textContent = "🚀 Mở module"; }
  };
}

// ------------------------------------------------------------ 🌳 Sơ đồ cây
function tree() {
  page(`<iframe class="tree-frame" src="/tree" title="Sơ đồ cây tri thức Digital Twin"></iframe>`);
}

// ------------------------------------------------------------ 🤖 Hỏi phòng R&D
async function ask() {
  const [hist, mods] = await Promise.all([get("/api/chat"), get("/api/modules")]);
  MODS = mods;
  const who = k => TEAM.find(p => p.key === (k || "director")) || TEAM[0];
  const mod = MODS.find(m => m.id === askModule);
  const pool = TEAM.filter(p => p.key === "director" || !mod || p.module === mod.id || (mod.shared || []).includes(p.key));
  if (askAgent && !pool.some(p => p.key === askAgent)) askAgent = null;
  page(`
    <div class="card">
      <div class="card-head"><h3>🤖 Hỏi phòng R&amp;D</h3><div class="row"><a class="btn" href="/api/chat.docx?i=all" download>📄 Xuất tất cả ra Word</a><button class="btn" id="clear">🧹 Xóa lịch sử</button></div></div>
      <div class="agent-picker" id="mod-pick"><button data-m="" class="${!mod ? "on" : ""}">🏢 Cả phòng</button>${MODS.map(m => `<button data-m="${esc(m.id)}" class="${mod && mod.id === m.id ? "on" : ""}">${esc(m.icon)} ${esc(m.name)}</button>`).join("")}</div>
      <div class="agent-picker">${pool.map(p => `<button data-k="${p.key}" class="${(askAgent || "director") === p.key ? "on" : ""}" title="${esc(p.role)}">${avatar(p, 26)} ${p.module_icon && !mod ? esc(p.module_icon) + " " : ""}${esc(p.name)}</button>`).join("")}</div>
      <p class="small muted" id="who-hint"></p>
      <textarea id="q" placeholder="Ví dụ: So sánh kiến trúc DT của Hitachi Lumada APM và Siemens Sensformer; cái nào phù hợp lưới 110 kV Việt Nam?"></textarea>
      <div class="row" style="margin-top:10px;justify-content:space-between">
        <span class="small muted"><label style="cursor:pointer"><input type="checkbox" id="use-web" ${STATUS?.web?.enabled === false ? "" : "checked"}> 🌐 Tra thêm Internet (ưu tiên web chính thức)</label> · ⌘/Ctrl + Enter để gửi · dữ liệu khách hàng (06_vti_data) không gửi ra Internet</span>
        <button class="btn btn-primary" id="send">Gửi câu hỏi</button>
      </div>
    </div>
    <div class="chat" id="chat" style="margin-top:16px"></div>`);
  const hint = () => {
    const p = who(askAgent);
    $("#who-hint").textContent = (askAgent ? `Hỏi trực tiếp ${p.name} – ${p.role} (tra kho tài liệu + Internet, Qwen tổng hợp, có trích nguồn).` : `Trưởng phòng Minh chọn chuyên viên phù hợp${mod ? " trong module " + mod.name : " trong cả phòng"}, tra kho tài liệu + website chính thức (hãng, IEC/IEEE/CIGRE, EVN…) rồi trả lời có trích nguồn [S#]/[W#]; chi tiết không có nguồn sẽ bị đánh dấu CHƯA XÁC MINH.`);
  };
  hint();
  const bubble = (it, idx) => `
    <div class="msg me">${esc(it.q)}</div>
    <div class="msg bot"><div class="meta">${avatar(who(it.agent), 22)} <b>${esc(who(it.agent).name)}</b> · ${esc(it.time)} <span class="pill">${esc(it.engine || "local")}</span>${it.module ? ` <span class="pill">${esc((MODS.find(m => m.id === it.module) || {}).icon || "")} ${esc(it.module)}</span>` : ""}
      <a class="small" style="margin-left:auto" href="/api/chat.docx?i=${idx}" download>📄 Xuất Word</a></div>
      <div class="md">${it.a_html}</div></div>`;
  const chat = $("#chat");
  chat.innerHTML = hist.map((it, i) => bubble(it, i)).reverse().join("");
  view().querySelectorAll("#mod-pick button").forEach(b => b.onclick = () => { askModule = b.dataset.m; ask(); });
  view().querySelectorAll(".agent-picker button[data-k]").forEach(b => b.onclick = () => {
    askAgent = b.dataset.k === "director" ? null : b.dataset.k;
    view().querySelectorAll(".agent-picker button[data-k]").forEach(x => x.classList.toggle("on", x === b));
    hint();
  });
  $("#clear").onclick = async () => { if (confirm("Xóa toàn bộ lịch sử hỏi đáp?")) { await post("/api/chat/clear"); ask(); } };
  const send = async () => {
    const q = $("#q").value.trim();
    if (!q) return;
    const btn = $("#send");
    btn.disabled = true; btn.innerHTML = `<span class="spin"></span> Đang suy nghĩ…`;
    const pending = document.createElement("div");
    pending.innerHTML = `<div class="msg me">${esc(q)}</div><div class="msg bot"><span class="spin"></span> ${esc(who(askAgent).name)} đang tra tài liệu và soạn câu trả lời…</div>`;
    chat.prepend(pending);
    try {
      const { job } = await post("/api/ask", { question: q, agent: askAgent, module: askModule || null, web: $("#use-web") ? $("#use-web").checked : null });
      refreshChips();
      const it = await waitJob(job);
      pending.outerHTML = bubble(it, hist.length);
      hist.push(it);
      $("#q").value = "";
    } catch (e) { pending.remove(); toast("Lỗi: " + e.message, true); }
    btn.disabled = false; btn.textContent = "Gửi câu hỏi";
    refreshChips();
  };
  $("#send").onclick = send;
  $("#q").addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) send(); });
  $("#q").focus();
}


// ------------------------------------------------------------ 📰 Tin tức & Cơ hội
const NEWS_FILTERS = [
  ["opp", "🎯 Cơ hội VTI"], ["all", "Tất cả"], ["tender", "📝 Đấu thầu"], ["project", "🏗 Dự án & kế hoạch"],
  ["vn", "🇻🇳 Trong nước"], ["intl", "🌏 Quốc tế"], ["research", "🔬 Nghiên cứu"],
];
let newsFilter = "opp";

async function newsView(arg) {
  const r = await get("/api/news" + (arg ? "?date=" + encodeURIComponent(arg) : ""));
  const d = r.digest;
  page(`
    <div class="card">
      <div class="card-head"><h3>📰 Bản tin năng lượng & cơ hội hợp tác cho VTI</h3>
        <div class="row">
          ${r.days.length ? `<select id="nday">${r.days.map(x => `<option ${d && x === d.date ? "selected" : ""}>${x}</option>`).join("")}</select>` : ""}
          <button class="btn btn-primary" id="nref" ${r.running ? "disabled" : ""}>${r.running ? '<span class="spin"></span> Đang cập nhật…' : "🔄 Cập nhật ngay"}</button>
          ${d ? `<a class="btn" href="/api/news.docx?date=${d.date}" download>📄 Word</a>` : ""}
        </div></div>
      <p class="small muted">Tự cập nhật mỗi sáng (giờ đặt trong <code>config/news.yaml</code>) từ Google News (truy vấn tiếng Việt và tiếng Anh), các trang ngành và arXiv. Mỗi tin được chấm điểm mức liên quan tới năng lực VTI (giám sát online, MBA, trạm, DGA, PD, DT…) và tín hiệu cơ hội (đấu thầu, khởi công, hợp tác…). Qwen viết tóm tắt + gợi ý hành động cho các tin điểm cao.</p>
      ${d ? `<div class="small muted">Cập nhật ${esc(d.fetched_at.replace("T", " "))} · ${d.items.length} tin · ${d.sources.filter(x => x.ok).length}/${d.sources.length} nguồn hoạt động${d.ai_at ? " · AI " + esc(d.ai_at.slice(11)) : ""}</div>` : ""}
      <pre class="log" id="nlog" hidden></pre>
    </div>
    ${d ? `<div class="agent-picker" style="margin-top:14px">${NEWS_FILTERS.map(([k, l]) => `<button data-f="${k}" class="${k === newsFilter ? "on" : ""}">${l} <span class="pill">${newsCount(d, k)}</span></button>`).join("")}</div>
    <input id="nq" placeholder="Lọc theo từ khóa: EVN, 110kV, BESS, Hitachi…" style="width:100%;margin-bottom:12px">
    <div class="list" id="nlist"></div>
    <details class="card" style="margin-top:14px"><summary class="small">Tình trạng ${d.sources.length} nguồn tin</summary>
      <ul class="small">${d.sources.map(x => `<li>${x.ok ? "✅" : "⚠️"} ${esc(x.name)} – ${x.count} tin${x.error ? " · " + esc(x.error) : ""}</li>`).join("")}</ul></details>`
    : `<div class="card" style="margin-top:14px"><p>Chưa có bản tin nào. Bấm <b>🔄 Cập nhật ngay</b> (cần Internet; khoảng 1–2 phút, phần AI thêm vài phút).</p></div>`}`);
  if ($("#nday")) $("#nday").onchange = e => (location.hash = "news:" + e.target.value);
  $("#nref").onclick = async () => {
    const btn = $("#nref"), log = $("#nlog");
    btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Đang cập nhật…'; log.hidden = false;
    try {
      const { job } = await post("/api/news/refresh", { ai: true });
      await waitJob(job, l => { log.textContent = l.slice(-14).join("\n"); });
      toast("✅ Đã cập nhật bản tin");
      newsView();
    } catch (e) { toast("Lỗi cập nhật tin: " + e.message, true); btn.disabled = false; btn.textContent = "🔄 Cập nhật ngay"; }
  };
  if (!d) return;
  const draw = () => {
    const q = ($("#nq").value || "").toLowerCase();
    const items = newsPick(d, newsFilter).filter(x => !q || (x.title + " " + x.summary + " " + x.publisher).toLowerCase().includes(q));
    $("#nlist").innerHTML = items.slice(0, 120).map(x => `
      <div class="card" style="padding:14px 16px">
        <div class="row" style="justify-content:space-between;align-items:flex-start">
          <a href="${esc(x.link)}" target="_blank" rel="noopener" style="font-weight:700;color:var(--ink);text-decoration:none;flex:1">${esc(x.title)}</a>
          ${x.is_opportunity ? '<span class="pill warn">🎯 Cơ hội</span>' : ""}
        </div>
        <div class="small muted" style="margin:4px 0">${esc(x.publisher)} · ${esc((x.published || "").slice(0, 16).replace("T", " "))} · <span class="pill">${esc(x.category_vi)}</span> <span class="pill">${x.region === "vn" ? "Trong nước" : "Quốc tế"}</span> · điểm ${x.score}</div>
        ${x.ai ? `<div class="small"><b>Tóm tắt:</b> ${esc(x.ai.tom_tat)}<br><b>Cơ hội VTI:</b> ${esc(x.ai.co_hoi)}<br><b>Việc nên làm:</b> ${esc(x.ai.hanh_dong)} <span class="pill">AI · Qwen</span></div>`
               : (x.summary && x.summary !== x.title ? `<div class="small muted">${esc(x.summary.slice(0, 260))}</div>` : "")}
        ${x.reasons.length ? `<div class="small muted" style="margin-top:4px">↳ ${esc(x.reasons.join(" · "))}</div>` : ""}
      </div>`).join("") || '<div class="card muted">Không có tin phù hợp bộ lọc.</div>';
  };
  view().querySelectorAll("[data-f]").forEach(b => b.onclick = () => {
    newsFilter = b.dataset.f;
    view().querySelectorAll("[data-f]").forEach(x => x.classList.toggle("on", x === b));
    draw();
  });
  $("#nq").oninput = draw;
  draw();
}

function newsPick(d, f) {
  const it = d.items;
  if (f === "opp") return it.filter(x => x.is_opportunity);
  if (f === "tender" || f === "project" || f === "research") return it.filter(x => x.category === f);
  if (f === "vn" || f === "intl") return it.filter(x => x.region === f && x.category !== "research");
  return it;
}
function newsCount(d, f) { return newsPick(d, f).length; }

// ------------------------------------------------------------ 📑 Báo cáo
async function reports(arg) {
  const list = await get("/api/reports");
  const sel = arg ? decodeURIComponent(arg) : list[0]?.path;
  page(`<div class="split">
      <div class="list sticky">${list.map(r => `<div class="list-item ${r.path === sel ? "on" : ""}" data-p="${esc(r.path)}">
        <div><b>${esc(r.title)}</b><div class="small muted">${esc(r.mtime)}</div></div><span class="pill">${esc(r.week)}</span></div>`).join("") || `<div class="card muted">Chưa có báo cáo.</div>`}
      </div>
      <div class="card md" id="rep"><p class="muted">Chọn một báo cáo…</p></div></div>`);
  view().querySelectorAll(".list-item").forEach(d => d.onclick = () => (location.hash = "reports:" + encodeURIComponent(d.dataset.p)));
  if (sel) {
    const r = await get("/api/report?path=" + encodeURIComponent(sel));
    $("#rep").innerHTML = `<div class="card-head"><h2 style="margin:0">${esc(r.title)}</h2>
      <a class="btn btn-primary" href="/api/report.docx?path=${encodeURIComponent(r.path)}" download>📄 Xuất Word</a></div>
      <div class="small muted" style="margin-bottom:8px">${esc(r.path)}</div>${r.html}`;
  }
}

// ------------------------------------------------------------ 👥 Nhân sự
function personCard(p) {
  const li = a => (a || []).map(x => `<li>${esc(x)}</li>`).join("");
  return `<div class="card"><div class="person">${avatar(p, 64)}
      <div style="flex:1"><h3>${esc(p.name)}</h3><div class="role">${esc(p.role)}</div>
        <p class="small" style="margin:6px 0">${esc(p.scope)}</p>
        ${p.task ? `<div class="small"><span class="pill">Đang làm</span> ${esc(p.task)}</div>` : ""}
        ${p.references?.length ? `<div class="small muted" style="margin-top:8px"><b>Tài liệu gốc:</b><ul>${li(p.references)}</ul></div>` : ""}
        ${p.questions?.length ? `<div class="small muted"><b>Câu hỏi thường trực:</b><ul>${li(p.questions)}</ul></div>` : ""}
        <button class="btn" style="margin-top:10px" data-k="${p.key}">🤖 Hỏi ${esc(p.name)}</button>
      </div></div></div>`;
}

async function team() {
  MODS = await get("/api/modules");
  const groups = [["director", "🏢 Ban điều phối"], ["shared", "🤝 Khối chuyên viên dùng chung (mọi module mượn được)"],
    ...MODS.map(m => [m.id, `${m.icon} Module ${m.name} · ${m.status_vi}`])];
  page(groups.map(([k, title]) => {
    const ps = TEAM.filter(p => p.module === k);
    return ps.length ? `<h2 class="section-h">${esc(title)} <span class="pill">${ps.length}</span></h2><div class="grid g2">${ps.map(personCard).join("")}</div>` : "";
  }).join(""));
  view().querySelectorAll("button[data-k]").forEach(b => b.onclick = () => {
    const p = TEAM.find(x => x.key === b.dataset.k);
    askAgent = b.dataset.k === "director" ? null : b.dataset.k;
    askModule = p && !["shared", "director"].includes(p.module) ? p.module : "";
    location.hash = "ask";
  });
}

// ------------------------------------------------------------ 🧮 Công cụ
function lineChart(series, keys) {
  const W = 760, H = 260, P = 36;
  const xs = series.map(r => r.t_min / 60);
  const ys = series.flatMap(r => keys.map(k => r[k.key]));
  const xmax = Math.max(...xs), ymin = Math.min(0, ...ys), ymax = Math.max(...ys) * 1.08;
  const X = x => P + (x / xmax) * (W - P - 10), Y = y => H - P + 10 - ((y - ymin) / (ymax - ymin)) * (H - P - 10);
  const grid = [0, .25, .5, .75, 1].map(f => { const v = ymin + f * (ymax - ymin); return `<line x1="${P}" x2="${W - 10}" y1="${Y(v)}" y2="${Y(v)}" stroke="#E7E7F1"/><text x="${P - 6}" y="${Y(v) + 4}" font-size="11" text-anchor="end" fill="#6B6B85">${Math.round(v)}</text>`; }).join("");
  const lines = keys.map(k => `<polyline fill="none" stroke="${k.color}" stroke-width="2.4" points="${series.map(r => `${X(r.t_min / 60).toFixed(1)},${Y(r[k.key]).toFixed(1)}`).join(" ")}"/>`).join("");
  const legend = keys.map((k, i) => `<g transform="translate(${P + 10 + i * 150},14)"><rect width="14" height="4" y="-4" fill="${k.color}"/><text x="20" font-size="12" fill="#1E1B3A">${k.label}</text></g>`).join("");
  return `<svg viewBox="0 0 ${W} ${H}">${grid}${lines}${legend}<text x="${W - 10}" y="${H - 6}" font-size="11" text-anchor="end" fill="#6B6B85">giờ</text></svg>`;
}

function tools() {
  page(`
    <div class="card">
      <div class="card-head"><h3>🌡 Mô hình nhiệt máy biến áp – IEC 60076-7</h3><span class="pill">Hot-spot & Loss of life</span></div>
      <div class="form-grid">
        <label class="f">Làm mát<select id="cool">${["ONAN", "ONAF", "OF", "OD"].map(c => `<option ${c === "ONAF" ? "selected" : ""}>${c}</option>`).join("")}</select></label>
        <label class="f">Tải K (pu)<input id="load" type="number" step="0.05" value="1.1"></label>
        <label class="f">Nhiệt độ môi trường θa (°C)<input id="amb" type="number" value="35"></label>
        <label class="f">R = Pk/P0<input id="R" type="number" step="0.5" value="6"></label>
        <label class="f">Δθor định mức (K)<input id="dtor" type="number" value="45"></label>
        <label class="f">Δθhr định mức (K)<input id="dthr" type="number" value="35"></label>
        <label class="f">Thời gian (h)<input id="hrs" type="number" value="24"></label>
      </div>
      <label class="f" style="margin-bottom:10px">Biểu đồ phụ tải 24 giờ (pu, cách nhau dấu phẩy – để trống = tải K không đổi)
        <input id="prof" placeholder="0.7,0.65,0.6,0.6,0.65,0.8,1.0,1.1,1.15,1.2,1.2,1.25,1.3,1.3,1.25,1.2,1.15,1.2,1.3,1.25,1.1,0.95,0.85,0.75"></label>
      <button class="btn btn-primary" id="run-th">Tính toán</button>
      <div id="th-out" style="margin-top:14px"></div>
    </div>

    <div class="grid g2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>🧪 Chẩn đoán DGA</h3><span class="pill">Duval T1 · IEC 60599</span></div>
        <div class="form-grid">${["h2:H₂:100", "ch4:CH₄:120", "c2h2:C₂H₂:1", "c2h4:C₂H₄:50", "c2h6:C₂H₆:65", "co:CO:", "co2:CO₂:"].map(s => { const [k, l, v] = s.split(":"); return `<label class="f">${l} (ppm)<input id="g-${k}" type="number" value="${v}" placeholder="tùy chọn"></label>`; }).join("")}
          <label class="f">OLTC thông dầu với thùng chính<select id="g-oltc"><option value="">Không</option><option value="1">Có</option></select></label></div>
        <button class="btn btn-primary" id="run-dga">Chẩn đoán</button>
        <div id="dga-out" style="margin-top:14px"></div>
      </div>
      <div class="card">
        <div class="card-head"><h3>🏭 Đọc file SCD/SCL – IEC 61850-6</h3><span class="pill">Tìm LN giám sát</span></div>
        <div class="drop" id="scl-drop">Kéo thả file .scd / .icd / .cid vào đây hoặc bấm để chọn<input type="file" id="scl-file" accept=".scd,.icd,.cid,.ssd,.xml" hidden></div>
        <div id="scl-out" style="margin-top:14px"></div>
      </div>
    </div>`);

  $("#run-th").onclick = async () => {
    const prof = $("#prof").value.trim();
    const body = { cooling: $("#cool").value, load: +$("#load").value, ambient: +$("#amb").value, R: +$("#R").value, dtor: +$("#dtor").value, dthr: +$("#dthr").value, hours: +$("#hrs").value };
    if (prof) body.profile = prof.split(/[,;\s]+/).filter(Boolean).map(Number);
    try {
      const r = await post("/api/thermal", body);
      const lvl = r.max_theta_h > 140 ? "bad" : r.max_theta_h > 120 ? "warn" : "ok";
      $("#th-out").innerHTML = `
        <div class="grid g4">
          <div class="card stat"><div class="stat-value">${r.max_theta_h} °C</div><div class="stat-label">Hot-spot lớn nhất <span class="pill ${lvl}">${lvl === "ok" ? "an toàn" : lvl === "warn" ? "> 120 °C" : "> 140 °C"}</span></div></div>
          <div class="card stat"><div class="stat-value">${r.loss_of_life_h} h</div><div class="stat-label">Hao mòn tuổi thọ tương đương</div></div>
          <div class="card stat"><div class="stat-value">${r.max_load_120} pu</div><div class="stat-label">Tải max để θh ≤ 120 °C</div></div>
          <div class="card stat"><div class="stat-value">${r.max_load_140} pu</div><div class="stat-label">Tải max để θh ≤ 140 °C</div></div>
        </div>
        <div class="chart" style="margin-top:12px">${lineChart(r.series, [{ key: "theta_h", label: "θh điểm nóng", color: "#E11D48" }, { key: "theta_o", label: "θo dầu đỉnh", color: "#5B4BF5" }])}</div>
        <p class="small muted">Mô hình phương trình vi phân IEC 60076-7:2018 (Annex B/C), giấy cách điện nâng cấp nhiệt: V = exp(15000/383 − 15000/(θh+273)), tham chiếu 110 °C (giấy thường: V = 2^((θh−98)/6)). Thông số định mức lấy từ biên bản heat-run test.</p>`;
    } catch (e) { toast(e.message, true); }
  };

  $("#run-dga").onclick = async () => {
    const b = {}; ["h2", "ch4", "c2h2", "c2h4", "c2h6"].forEach(k => (b[k] = +$("#g-" + k).value));
    ["co", "co2"].forEach(k => { const v = $("#g-" + k).value; if (v !== "") b[k] = +v; });
    b.oltc = $("#g-oltc").value;
    try {
      const r = await post("/api/dga", b);
      const ty = r.typical;
      const tyHtml = ty.status === "normal"
        ? `<p><span class="pill ok">Mọi khí dưới giá trị điển hình IEC 60599 (Bảng A.2) → DGA bình thường</span> – theo Điều 9 không cần chẩn đoán loại lỗi; kết quả tỷ số bên dưới chỉ để tham khảo.</p>`
        : `<p><span class="pill warn">Vượt giá trị điển hình:</span> ${ty.above.map(a => `${a.gas} = ${a.value} (> ${a.typical_upper})`).join(", ")} → tính tốc độ tăng khí và chẩn đoán loại lỗi.</p>`;
      $("#dga-out").innerHTML = tyHtml + (ty.paper_note ? `<p class="small">⚠️ ${esc(ty.paper_note)}</p>` : "") + `<div class="kv">
        <span>Duval Triangle 1</span><b>${esc(r.duval)} – ${esc(r.duval_desc)}</b>
        <span>% CH₄ / C₂H₄ / C₂H₂</span><span>${r.duval_pct.CH4} / ${r.duval_pct.C2H4} / ${r.duval_pct.C2H2}</span>
        <span>IEC 60599 (tỷ số)</span><b>${esc(r.iec60599)} – ${esc(r.iec60599_desc)}</b>
        <span>Tỷ số</span><span>${Object.entries(r.ratios).map(([k, v]) => `${k} = ${v}`).join(" · ")}</span>
        <span>Kết luận</span><span class="pill ${r.agree ? "ok" : "warn"}">${r.agree ? "Hai phương pháp thống nhất" : "Hai phương pháp khác nhau → cần xem xu hướng & lấy mẫu phòng thí nghiệm"}</span></div>
        <p class="small muted">Lưu ý (CIGRE TB 783): đa số thiết bị DGA online thử nghiệm đạt yêu cầu độ chính xác ±15 % của IEC nhưng một số không đạt; ở nồng độ thấp (&lt; 10 ppm) sai số có thể &gt; 50 % làm chẩn đoán vô nghĩa. Sai số hệ thống cũng làm sai tốc độ tăng khí → kiểm chứng thiết bị bằng mẫu chuẩn gas-in-oil và đối chiếu phòng thí nghiệm. Ngưỡng điển hình dùng cận trên Bảng A.2 – nên thay bằng giá trị điển hình của chính đội máy.</p>`;
    } catch (e) { toast(e.message, true); }
  };

  const drop = $("#scl-drop"), file = $("#scl-file");
  const upload = async f => {
    try {
      const r = await post("/api/scl", await f.arrayBuffer(), true);
      const subs = r.model.substations || [];
      $("#scl-out").innerHTML = `
        <div class="kv"><span>Trạm</span><b>${subs.map(s => esc(s.name)).join(", ") || "—"}</b>
          <span>IED</span><b>${r.model.ieds.length}</b>
          <span>Máy biến áp</span><b>${subs.flatMap(s => s.transformers).map(t => esc(t.name)).join(", ") || "—"}</b></div>
        <h4 style="margin:12px 0 6px">Tín hiệu giám sát tình trạng (condition monitoring)</h4>
        ${r.signals.length ? `<div class="md"><table><tr><th>IED</th><th>LN</th><th>Lớp</th><th>Ý nghĩa</th></tr>${r.signals.map(s => `<tr><td>${esc(s.ied)}</td><td>${esc(s.ln)}</td><td>${esc(s.class)}</td><td>${esc(s.meaning)}</td></tr>`).join("")}</table></div>` : `<p class="muted">Không thấy LN giám sát (SIML/SPDC/STMP/SIMG/…).</p>`}`;
    } catch (e) { toast("Không đọc được SCL: " + e.message, true); }
  };
  drop.onclick = () => file.click();
  file.onchange = () => file.files[0] && upload(file.files[0]);
  drop.ondragover = e => { e.preventDefault(); drop.classList.add("over"); };
  drop.ondragleave = () => drop.classList.remove("over");
  drop.ondrop = e => { e.preventDefault(); drop.classList.remove("over"); e.dataTransfer.files[0] && upload(e.dataTransfer.files[0]); };
}

// ------------------------------------------------------------ 📚 Kho tài liệu
const FOLDER_NAMES = { "01_standards": "Tiêu chuẩn IEC/ISO", "02_cigre_ieee": "CIGRE & IEEE", "03_vendor": "Tài liệu hãng", "04_vietnam": "Pháp lý & EVN", "05_papers": "Bài báo khoa học", "06_vti_data": "Dữ liệu VTI/khách hàng (chỉ local)" };

const folderLabel = d => d.module_name && d.folder.startsWith("m_") ? `${d.module_icon} ${d.module_name}` : (FOLDER_NAMES[d.folder] || d.folder);

async function library(arg) {
  const [lib, st] = await Promise.all([get("/api/library"), get("/api/status")]);
  const pre = arg ? decodeURIComponent(arg) : "";
  page(`
    <div class="card">
      <div class="card-head"><h3>📚 Kho tài liệu (RAG)</h3><span class="pill">${st.kb.documents} tài liệu · ${st.kb.chunks} đoạn đã nạp</span></div>
      <div class="row">
        <label class="f">Thư mục<select id="folder">${lib.map(d => `<option value="${esc(d.folder)}" ${d.folder === pre ? "selected" : ""}>${esc(d.folder)} – ${esc(folderLabel(d))}</option>`).join("")}</select></label>
      </div>
      <div class="drop" id="lib-drop" style="margin-top:10px">Kéo thả PDF / MD / TXT vào đây (nhiều file) hoặc bấm để chọn<input type="file" id="lib-file" multiple accept=".pdf,.md,.txt" hidden></div>
      <div class="row" style="margin-top:12px"><button class="btn btn-primary" id="ingest">⚙️ Nạp vào kho (tạo embedding)</button>
        <span class="small muted">PDF bản quyền chỉ nằm trên máy anh, không lên GitHub.</span></div>
      <pre class="log" id="ing-log" hidden></pre>
    </div>
    <div class="grid g3" style="margin-top:16px">${lib.map(d => `
      <div class="card"><div class="card-head"><h3>${d.folder === "06_vti_data" ? "🔒" : d.folder.startsWith("m_") ? "" : "📁"} ${esc(folderLabel(d))}</h3><span class="pill">${d.files.length}</span></div>
        <div class="small muted">${esc(d.folder)}</div>
        <ul class="small">${d.files.map(f => `<li>${esc(f.name)} <span class="muted">(${f.kb} KB)</span></li>`).join("") || "<li class='muted'>trống</li>"}</ul></div>`).join("")}</div>`);

  const drop = $("#lib-drop"), file = $("#lib-file");
  const upload = async files => {
    for (const f of files) {
      try {
        await post(`/api/upload?folder=${encodeURIComponent($("#folder").value)}&name=${encodeURIComponent(f.name)}`, await f.arrayBuffer(), true);
        toast("Đã lưu " + f.name);
      } catch (e) { toast(f.name + ": " + e.message, true); }
    }
    library();
  };
  drop.onclick = () => file.click();
  file.onchange = () => upload([...file.files]);
  drop.ondragover = e => { e.preventDefault(); drop.classList.add("over"); };
  drop.ondragleave = () => drop.classList.remove("over");
  drop.ondrop = e => { e.preventDefault(); drop.classList.remove("over"); upload([...e.dataTransfer.files]); };
  $("#ingest").onclick = async () => {
    const btn = $("#ingest"), log = $("#ing-log");
    btn.disabled = true; log.hidden = false; log.textContent = "Bắt đầu…";
    try {
      const { job } = await post("/api/ingest");
      const r = await waitJob(job, l => { log.textContent = l.join("\n"); log.scrollTop = log.scrollHeight; });
      toast(`✅ Nạp thêm ${r.added} tài liệu`);
      setTimeout(library, 800);
    } catch (e) { toast("Lỗi nạp tài liệu: " + e.message, true); btn.disabled = false; }
  };
}

// ------------------------------------------------------------ ⚙️ Hệ thống
async function settings() {
  const st = await get("/api/status");
  setTimeout(() => {
    const b = $("#web-check");
    if (b) b.onclick = async () => {
      b.disabled = true; b.innerHTML = '<span class="spin"></span> Đang kiểm tra…';
      try {
        const { job } = await post("/api/web/check", {});
        const r = await waitJob(job);
        $("#web-res").innerHTML = `<table class="tbl"><tr><th>Công cụ</th><th>Kết quả</th></tr>${r.checks.map(c => `<tr><td>${esc(c.engine)}</td><td>${c.ok ? "✅ " + c.results + (c.ms ? " kết quả · " + c.ms + " ms" : " ký tự") : "❌ " + esc(c.error || "không có kết quả")}</td></tr>`).join("")}</table>`;
      } catch (e) { toast(e.message, true); }
      b.disabled = false; b.textContent = "🩺 Kiểm tra kết nối web";
    };
  }, 0);
  page(`
    <div class="grid g2">
      <div class="card"><div class="card-head"><h3>🧠 Model AI</h3><span class="pill ${st.ollama_ok ? "ok" : "bad"}">${st.ollama_ok ? "Ollama đang chạy" : "Ollama chưa chạy"}</span></div>
        <div class="kv"><span>RAM máy</span><b>${st.ram_gb} GB</b><span>Model chat</span><b>${esc(st.chat_model)}</b><span>Model embedding</span><b>${esc(st.embed_model)}</b>
          <span>Model đã tải</span><span>${st.models.map(esc).join(", ") || "—"}</span></div>
        ${st.ollama_ok ? "" : `<p class="small">Mở app <b>Ollama</b> (hoặc chạy <code>ollama serve</code>) rồi tải lại trang.</p>`}</div>
      <div class="card"><div class="card-head"><h3>☁️ Cloud (ưu tiên miễn phí)</h3><span class="pill ${st.cloud.enabled ? "ok" : ""}">${st.cloud.enabled ? "Bật" : "Tắt"}</span></div>
        <div class="small">Lượt tiếp theo của Trưởng phòng sẽ chạy trên: <b>${esc(st.cloud.next)}</b></div>
        <ul class="small">${st.cloud.lines.map(l => `<li>${esc(l)}</li>`).join("")}</ul>
        <p class="small muted">Bật trong <code>config/settings.yaml → cloud.enabled: true</code> và đặt khóa API trong <code>.env</code>. Dữ liệu thư mục 06_vti_data luôn chạy local.</p></div>
    </div>
    <div class="card" style="margin-top:16px"><div class="card-head"><h3>🌐 Nghiên cứu Internet</h3><div class="row"><span class="pill ${st.web?.enabled ? "ok" : ""}">${st.web?.enabled ? "Bật" : "Tắt"}</span><button class="btn" id="web-check">🩺 Kiểm tra kết nối web</button></div></div>
      <p class="small">Khi hỏi đáp và trong chu kỳ 3 ngày, chuyên viên tra Bing/DuckDuckGo/OpenAlex, đọc trang (ưu tiên 🏛 website chính thức: hãng, IEC/IEEE/CIGRE, EVN, cơ quan nhà nước → ✅ báo chí/tạp chí uy tín → ⚠️ nguồn khác), trích dẫn [W#] kèm URL. Sau khi Qwen trả lời, app tự dò các số liệu/số hiệu tiêu chuẩn không có trong nguồn và gắn nhãn <b>CHƯA XÁC MINH</b>. Danh sách nguồn & hãng: <code>config/web_sources.yaml</code>.</p>
      <div id="web-res" class="small"></div></div>
    <div class="card" style="margin-top:16px"><div class="card-head"><h3>🧩 Tổ chức phòng</h3><a class="btn" href="#modules">Quản lý module</a></div>
      <div class="kv"><span>Module</span><b>${st.modules.total} (đang nghiên cứu ${st.modules.active})</b><span>Chu kỳ báo cáo</span><b>3 ngày/lần, tự chạy sau 07:00 khi Ollama đang chạy</b>
        <span>Cấu hình</span><span><code>config/modules.yaml</code> (module), <code>config/team.yaml</code> (Trưởng phòng + khối dùng chung), <code>config/settings.yaml → cycle</code></span></div></div>
    <div class="card" style="margin-top:16px"><div class="card-head"><h3>⌨️ Lệnh Terminal hữu ích</h3></div>
      <div class="md"><table>
        <tr><td><code>bash scripts/install_app.sh</code></td><td>Cài server luôn chạy nền (tự chạy chu kỳ báo cáo 3 ngày)</td></tr>
        <tr><td><code>python3 dtlab.py modules</code></td><td>Liệt kê module và trạng thái</td></tr>
        <tr><td><code>python3 dtlab.py module-status bess active</code></td><td>Kích hoạt / tạm dừng module</td></tr>
        <tr><td><code>python3 dtlab.py doctor</code></td><td>Kiểm tra Ollama, model, RAM</td></tr>
        <tr><td><code>python3 dtlab.py free-models</code></td><td>Xem quota model cloud miễn phí</td></tr>
        <tr><td><code>python3 dtlab.py cycle --modules dt,market</code></td><td>Chạy ngay một chu kỳ nghiên cứu từ Terminal</td></tr>
      </table></div></div>`);
}

// ------------------------------------------------------------ router
const VIEWS = { today, modules: modulesView, tree, ask, news: newsView, reports, team, tools, library, settings };

async function route() {
  const [name, arg] = (location.hash.slice(1) || "today").split(":");
  const fn = VIEWS[name] || today;
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === (VIEWS[name] ? name : "today")));
  try { await fn(arg); } catch (e) { page(`<div class="card"><h3>⚠️ Lỗi</h3><p>${esc(e.message)}</p></div>`); }
  window.scrollTo({ top: 0 });
}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => (location.hash = t.dataset.tab)));
window.addEventListener("hashchange", route);

(async function init() {
  try { TEAM = await get("/api/team"); } catch (e) { TEAM = []; }
  await route();
  refreshChips();
  setInterval(refreshChips, 15000);
})();
