// DT-RnD-Lab — router các tab (cùng kiểu EnglishCoach) + các màn hình
import { $, esc, get, post, toast, waitJob, fmtDate } from "./api.js";
import { drawOffice, avatar } from "./office.js";

const view = () => $("#view");
let TEAM = [];
let STATUS = null;
let askAgent = null; // agent đang chọn ở tab Hỏi

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
    const p = STATUS.phase;
    $("#phase-chip").textContent = `🧭 ${p.code} · ${p.name}`;
    const eng = STATUS.ollama_ok ? STATUS.chat_model : "Ollama chưa chạy";
    $("#engine-chip").textContent = `🧠 ${eng}${STATUS.cloud.enabled ? " + ☁️" : ""}`;
    $("#job-chip").hidden = !STATUS.jobs_running;
    $("#job-chip").textContent = `⏳ ${STATUS.jobs_running} việc đang chạy`;
  } catch (e) { /* server đang khởi động */ }
}

// ------------------------------------------------------------ 🏠 Hôm nay
async function today() {
  page(`<p class="muted">Đang tải…</p>`);
  const [st, reports] = await Promise.all([get("/api/status"), get("/api/reports")]);
  STATUS = st;
  const p = st.phase;
  const now = new Date().toISOString().slice(0, 10);
  const last = reports[0];
  page(`
    <div class="card hero">
      <h1 class="greet">${greetWord()} anh Khương đẹp trai 👋</h1>
      <p>Phòng R&amp;D Digital Twin đang ở <b>${p.code} – ${esc(p.name)}</b> (${fmtDate(p.start)} → ${fmtDate(p.end)}).</p>
      <div class="bar"><i style="width:${Math.round(p.pct * 100)}%"></i></div>
      <p class="small">${Math.round(p.pct * 100)}% thời gian giai đoạn · còn ${p.days_left} ngày · mục tiêu: hiểu sâu hệ thống Transformer DT &amp; Substation DT trước khi làm sản phẩm.</p>
      <div class="row" style="margin-top:12px">
        <button class="btn" id="go-ask">🤖 Hỏi phòng R&amp;D</button>
        <button class="btn" id="go-week">🗓 Chạy vòng nghiên cứu tuần</button>
        <button class="btn" id="go-tree">🌳 Mở sơ đồ cây</button>
      </div>
    </div>

    <div class="card scene-wrap" style="margin-top:16px"><div id="office"></div></div>
    <p class="small muted" style="margin:6px 4px">Bấm vào một người để giao câu hỏi trực tiếp cho người đó.</p>

    <div class="grid g4" style="margin-top:12px">
      <div class="card stat"><div class="stat-value">${st.reports}</div><div class="stat-label">Báo cáo đã có</div></div>
      <div class="card stat"><div class="stat-value">${st.kb.documents}</div><div class="stat-label">Tài liệu trong kho (${st.kb.chunks} đoạn)</div></div>
      <div class="card stat"><div class="stat-value">${st.ollama_ok ? "✅" : "⚠️"}</div><div class="stat-label">${st.ollama_ok ? "Qwen local sẵn sàng" : "Ollama chưa chạy"}</div></div>
      <div class="card stat"><div class="stat-value">${st.cloud.enabled ? "☁️" : "🔒"}</div><div class="stat-label">${st.cloud.enabled ? "Cloud miễn phí: bật" : "Chỉ chạy local"}</div></div>
    </div>

    <h2 class="section-h">🧭 Lộ trình nghiên cứu 5 giai đoạn</h2>
    <div class="phases">${p.all.map(x => `
      <div class="phase ${x.code === p.code ? "now" : x.end < now ? "done" : ""}">
        <b>${x.code} · ${esc(x.name)}</b><span class="small muted">${fmtDate(x.start)} → ${fmtDate(x.end)}</span>
      </div>`).join("")}</div>

    <h2 class="section-h">📑 Báo cáo mới nhất</h2>
    ${last ? `<div class="card click" id="last-rep"><div class="card-head"><h3>${esc(last.title)}</h3><div class="row"><span class="pill">${esc(last.week)}</span><a class="btn" id="last-docx" href="/api/report.docx?path=${encodeURIComponent(last.path)}" download>📄 Word</a></div></div>
      <div class="small muted">Cập nhật ${esc(last.mtime)} · bấm để đọc</div></div>` : `<div class="card muted">Chưa có báo cáo. Bấm “Chạy vòng nghiên cứu tuần”.</div>`}
  `);
  drawOffice($("#office"), TEAM, pk => { askAgent = pk.key === "director" ? null : pk.key; location.hash = "ask"; });
  $("#go-ask").onclick = () => (location.hash = "ask");
  $("#go-tree").onclick = () => (location.hash = "tree");
  $("#go-week").onclick = runWeek;
  if (last) {
    $("#last-rep").onclick = () => (location.hash = "reports:" + encodeURIComponent(last.path));
    $("#last-docx").onclick = e => e.stopPropagation();
  }
}

async function runWeek() {
  const focus = prompt("Trọng tâm tuần này (để trống = theo lộ trình):", "") ?? null;
  if (focus === null) return;
  try {
    const { job } = await post("/api/week", { focus });
    toast("Đã giao việc cho cả phòng. Qwen local có thể mất 15–40 phút…");
    refreshChips();
    const res = await waitJob(job);
    toast("✅ Xong báo cáo tuần: " + res.path);
    location.hash = "reports:" + encodeURIComponent(res.path);
  } catch (e) { toast("Lỗi vòng tuần: " + e.message, true); }
  refreshChips();
}

// ------------------------------------------------------------ 🌳 Sơ đồ cây
function tree() {
  page(`<iframe class="tree-frame" src="/tree" title="Sơ đồ cây tri thức Digital Twin"></iframe>`);
}

// ------------------------------------------------------------ 🤖 Hỏi phòng R&D
async function ask() {
  const hist = await get("/api/chat");
  const who = k => TEAM.find(p => p.key === (k || "director")) || TEAM[0];
  page(`
    <div class="card">
      <div class="card-head"><h3>🤖 Hỏi phòng R&amp;D</h3><div class="row"><a class="btn" href="/api/chat.docx?i=all" download>📄 Xuất tất cả ra Word</a><button class="btn" id="clear">🧹 Xóa lịch sử</button></div></div>
      <div class="agent-picker">${TEAM.map(p => `<button data-k="${p.key}" class="${(askAgent || "director") === p.key ? "on" : ""}">${avatar(p, 26)} ${esc(p.name)}</button>`).join("")}</div>
      <p class="small muted" id="who-hint"></p>
      <textarea id="q" placeholder="Ví dụ: So sánh kiến trúc DT của Hitachi Lumada APM và Siemens Sensformer; cái nào phù hợp lưới 110 kV Việt Nam?"></textarea>
      <div class="row" style="margin-top:10px;justify-content:space-between">
        <span class="small muted">⌘/Ctrl + Enter để gửi · dữ liệu khách hàng (06_vti_data) luôn xử lý local</span>
        <button class="btn btn-primary" id="send">Gửi câu hỏi</button>
      </div>
    </div>
    <div class="chat" id="chat" style="margin-top:16px"></div>`);
  const hint = () => {
    const p = who(askAgent);
    $("#who-hint").textContent = askAgent ? `Hỏi trực tiếp ${p.name} – ${p.role} (tra kho tài liệu + Qwen).` : "Trưởng phòng Minh sẽ trả lời tổng hợp, dựa trên kho tài liệu.";
  };
  hint();
  const bubble = (it, idx) => `
    <div class="msg me">${esc(it.q)}</div>
    <div class="msg bot"><div class="meta">${avatar(who(it.agent), 22)} <b>${esc(who(it.agent).name)}</b> · ${esc(it.time)} <span class="pill">${esc(it.engine || "local")}</span>
      <a class="small" style="margin-left:auto" href="/api/chat.docx?i=${idx}" download>📄 Xuất Word</a></div>
      <div class="md">${it.a_html}</div></div>`;
  const chat = $("#chat");
  chat.innerHTML = hist.map((it, i) => bubble(it, i)).reverse().join("");
  view().querySelectorAll(".agent-picker button").forEach(b => b.onclick = () => {
    askAgent = b.dataset.k === "director" ? null : b.dataset.k;
    view().querySelectorAll(".agent-picker button").forEach(x => x.classList.toggle("on", x === b));
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
      const { job } = await post("/api/ask", { question: q, agent: askAgent });
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
function team() {
  const li = a => (a || []).map(x => `<li>${esc(x)}</li>`).join("");
  page(`<div class="grid g2">${TEAM.map(p => `
    <div class="card"><div class="person">${avatar(p, 64)}
      <div style="flex:1"><h3>${esc(p.name)}</h3><div class="role">${esc(p.role)}</div>
        <p class="small" style="margin:6px 0">${esc(p.scope)}</p>
        <div class="small"><span class="pill">Đang làm</span> ${esc(p.task)}</div>
        ${p.references?.length ? `<div class="small muted" style="margin-top:8px"><b>Tài liệu gốc:</b><ul>${li(p.references)}</ul></div>` : ""}
        ${p.questions?.length ? `<div class="small muted"><b>Câu hỏi thường trực:</b><ul>${li(p.questions)}</ul></div>` : ""}
        <button class="btn" style="margin-top:10px" data-k="${p.key}">🤖 Hỏi ${esc(p.name)}</button>
      </div></div></div>`).join("")}</div>`);
  view().querySelectorAll("button[data-k]").forEach(b => b.onclick = () => { askAgent = b.dataset.k === "director" ? null : b.dataset.k; location.hash = "ask"; });
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

async function library() {
  const [lib, st] = await Promise.all([get("/api/library"), get("/api/status")]);
  page(`
    <div class="card">
      <div class="card-head"><h3>📚 Kho tài liệu (RAG)</h3><span class="pill">${st.kb.documents} tài liệu · ${st.kb.chunks} đoạn đã nạp</span></div>
      <div class="row">
        <label class="f">Thư mục<select id="folder">${lib.map(d => `<option value="${esc(d.folder)}">${esc(d.folder)} – ${esc(FOLDER_NAMES[d.folder] || "")}</option>`).join("")}</select></label>
      </div>
      <div class="drop" id="lib-drop" style="margin-top:10px">Kéo thả PDF / MD / TXT vào đây (nhiều file) hoặc bấm để chọn<input type="file" id="lib-file" multiple accept=".pdf,.md,.txt" hidden></div>
      <div class="row" style="margin-top:12px"><button class="btn btn-primary" id="ingest">⚙️ Nạp vào kho (tạo embedding)</button>
        <span class="small muted">PDF bản quyền chỉ nằm trên máy anh, không lên GitHub.</span></div>
      <pre class="log" id="ing-log" hidden></pre>
    </div>
    <div class="grid g3" style="margin-top:16px">${lib.map(d => `
      <div class="card"><div class="card-head"><h3>${d.folder === "06_vti_data" ? "🔒" : "📁"} ${esc(FOLDER_NAMES[d.folder] || d.folder)}</h3><span class="pill">${d.files.length}</span></div>
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
    <div class="card" style="margin-top:16px"><div class="card-head"><h3>🗂 Dự án</h3></div>
      <div class="kv"><span>Tên</span><b>${esc(st.project.name || "")}</b><span>Giai đoạn hiện tại</span><b>${esc(st.phase.code)} – ${esc(st.phase.name)}</b><span>Mốc hoàn thành hồ sơ</span><b>${esc(st.project.deadline || "")}</b></div></div>
    <div class="card" style="margin-top:16px"><div class="card-head"><h3>⌨️ Lệnh Terminal hữu ích</h3></div>
      <div class="md"><table>
        <tr><td><code>bash scripts/install_app.sh</code></td><td>Cài server luôn chạy nền + lịch báo cáo sáng thứ Hai</td></tr>
        <tr><td><code>python3 dtlab.py doctor</code></td><td>Kiểm tra Ollama, model, RAM</td></tr>
        <tr><td><code>python3 dtlab.py free-models</code></td><td>Xem quota model cloud miễn phí</td></tr>
        <tr><td><code>python3 dtlab.py week</code></td><td>Chạy vòng nghiên cứu tuần từ Terminal</td></tr>
      </table></div></div>`);
}

// ------------------------------------------------------------ router
const VIEWS = { today, tree, ask, reports, team, tools, library, settings };

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
