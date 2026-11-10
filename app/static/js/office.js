// Phòng làm việc minh họa: trưởng phòng đứng ở bảng, các chuyên viên ngồi máy (số người thay đổi theo module, SVG thuần)
const NS = "http://www.w3.org/2000/svg";
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

export function hairPath(style, cx, cy) {
  switch (style) {
    case "bun": return `M${cx - 15},${cy - 2} Q${cx - 16},${cy - 19} ${cx},${cy - 19} Q${cx + 16},${cy - 19} ${cx + 15},${cy - 2} Q${cx + 6},${cy - 12} ${cx - 15},${cy - 2} Z M${cx + 6},${cy - 22} a7,7 0 1,0 0.1,0 Z`;
    case "long": return `M${cx - 16},${cy + 14} Q${cx - 19},${cy - 20} ${cx},${cy - 19} Q${cx + 19},${cy - 20} ${cx + 16},${cy + 14} L${cx + 11},${cy + 14} Q${cx + 12},${cy - 6} ${cx},${cy - 9} Q${cx - 12},${cy - 6} ${cx - 11},${cy + 14} Z`;
    case "bob": return `M${cx - 16},${cy + 6} Q${cx - 18},${cy - 20} ${cx},${cy - 19} Q${cx + 18},${cy - 20} ${cx + 16},${cy + 6} L${cx + 12},${cy + 6} Q${cx + 10},${cy - 9} ${cx},${cy - 10} Q${cx - 10},${cy - 9} ${cx - 12},${cy + 6} Z`;
    case "buzz": return `M${cx - 14},${cy - 4} Q${cx - 14},${cy - 17} ${cx},${cy - 17} Q${cx + 14},${cy - 17} ${cx + 14},${cy - 4} Q${cx},${cy - 10} ${cx - 14},${cy - 4} Z`;
    case "side": return `M${cx - 15},${cy - 1} Q${cx - 16},${cy - 20} ${cx + 2},${cy - 19} Q${cx + 17},${cy - 18} ${cx + 15},${cy - 3} Q${cx + 4},${cy - 15} ${cx - 15},${cy - 1} Z`;
    default: return `M${cx - 15},${cy - 2} Q${cx - 15},${cy - 19} ${cx},${cy - 19} Q${cx + 15},${cy - 19} ${cx + 15},${cy - 2} Q${cx + 2},${cy - 12} ${cx - 15},${cy - 2} Z`;
  }
}

// Ảnh đại diện tròn nhỏ (chuỗi SVG) cho thẻ, chat
export function avatar(p, size = 34) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 34 34" aria-hidden="true"><circle cx="17" cy="17" r="16" fill="${p.look.shirt}"/><circle cx="17" cy="15" r="8" fill="${p.look.skin}"/><path d="${hairPath(p.look.style, 0, 0)}" transform="translate(17,15) scale(.533)" fill="${p.look.hair}"/></svg>`;
}

function head(g, cx, cy, L) {
  el("circle", { cx, cy, r: 15, fill: L.skin }, g);
  el("path", { d: hairPath(L.style, cx, cy), fill: L.hair }, g);
  el("circle", { cx: cx - 5, cy: cy + 2, r: 1.6, fill: "#1b1b1b" }, g);
  el("circle", { cx: cx + 5, cy: cy + 2, r: 1.6, fill: "#1b1b1b" }, g);
  el("path", { d: `M${cx - 4},${cy + 8} Q${cx},${cy + 11} ${cx + 4},${cy + 8}`, stroke: "#7a3b2e", "stroke-width": 1.3, fill: "none" }, g);
  if (L.glasses) {
    el("circle", { cx: cx - 5, cy: cy + 2, r: 4.2, fill: "none", stroke: "#222", "stroke-width": 1.2 }, g);
    el("circle", { cx: cx + 5, cy: cy + 2, r: 4.2, fill: "none", stroke: "#222", "stroke-width": 1.2 }, g);
    el("path", { d: `M${cx - 1},${cy + 2} L${cx + 1},${cy + 2}`, stroke: "#222", "stroke-width": 1.2 }, g);
  }
}

function person(svg, p, x, floor, standing, onPick) {
  const L = p.look;
  const g0 = el("g", { tabindex: 0, role: "button", "aria-label": `${p.name} – ${p.role}`, style: "cursor:pointer" }, svg);
  el("title", {}, g0).textContent = `${p.name} – ${p.role}\nĐang làm: ${p.task}`;
  const ink = css("--ink");
  if (standing) {
    const b = el("g", { class: "typing" }, g0);
    el("rect", { x: x - 9, y: floor - 46, width: 7, height: 46, rx: 3, fill: ink }, b);
    el("rect", { x: x + 2, y: floor - 46, width: 7, height: 46, rx: 3, fill: ink }, b);
    el("rect", { x: x - 17, y: floor - 104, width: 34, height: 62, rx: 12, fill: L.shirt }, b);
    el("path", { d: `M${x - 14},${floor - 94} L${x - 46},${floor - 128}`, stroke: L.shirt, "stroke-width": 8, "stroke-linecap": "round" }, b);
    el("path", { d: `M${x - 46},${floor - 128} L${x - 60},${floor - 142}`, stroke: css("--accent"), "stroke-width": 2.5, "stroke-linecap": "round" }, b);
    el("circle", { cx: x - 46, cy: floor - 128, r: 4.5, fill: L.skin }, b);
    head(b, x, floor - 120, L);
    el("text", { x, y: floor + 24, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: ink }, g0).textContent = `${p.name} · Trưởng phòng`;
  } else {
    el("rect", { x: x - 20, y: floor - 70, width: 40, height: 50, rx: 8, fill: css("--muted"), opacity: .35 }, g0);
    const b = el("g", { class: "typing", style: `animation-delay:${(x % 7) / 10}s` }, g0);
    el("rect", { x: x - 16, y: floor - 78, width: 32, height: 44, rx: 11, fill: L.shirt }, b);
    head(b, x, floor - 92, L);
    el("rect", { x: x - 46, y: floor - 34, width: 92, height: 8, rx: 2, fill: css("--desk") }, g0);
    el("rect", { x: x - 40, y: floor - 26, width: 5, height: 26, fill: css("--desk") }, g0);
    el("rect", { x: x + 35, y: floor - 26, width: 5, height: 26, fill: css("--desk") }, g0);
    el("rect", { x: x - 30, y: floor - 70, width: 60, height: 36, rx: 3, fill: ink }, g0);
    const sc = el("g", { class: "screen" }, g0);
    el("rect", { x: x - 27, y: floor - 67, width: 54, height: 28, rx: 2, fill: css("--primary-2"), opacity: .9 }, sc);
    el("polyline", { points: `${x - 23},${floor - 45} ${x - 14},${floor - 52} ${x - 6},${floor - 48} ${x + 3},${floor - 60} ${x + 12},${floor - 54} ${x + 22},${floor - 62}`, fill: "none", stroke: "#fff", "stroke-width": 1.6 }, sc);
    el("text", { x, y: floor + 20, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: ink }, g0).textContent = (p.module_icon ? p.module_icon + " " : "") + p.name;
  }
  const by = standing ? floor - 170 : floor - 138, bx = standing ? x + 8 : x - 22;
  el("rect", { x: bx, y: by, width: 44, height: 20, rx: 10, fill: "#fff", stroke: css("--line") }, g0);
  [0, 1, 2].forEach(i => el("circle", { class: "dot", cx: bx + 12 + i * 10, cy: by + 10, r: 2.6, fill: css("--accent") }, g0));
  const pick = () => onPick && onPick(p);
  g0.addEventListener("click", pick);
  g0.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
}

export function drawOffice(host, team, onPick) {
  host.innerHTML = "";
  const nStaff = team.filter(p => p.key !== "director").length;
  const W = Math.max(1100, 320 + nStaff * 108 + 230);
  const svg = el("svg", { viewBox: `0 0 ${W} 300`, role: "img", "aria-label": "Phòng R&D VTI đang làm việc" }, host);
  el("rect", { x: 0, y: 0, width: W, height: 210, fill: css("--wall") }, svg);
  el("rect", { x: 0, y: 210, width: W, height: 90, fill: css("--floor") }, svg);
  // cửa sổ: lưới truyền tải
  const win = el("g", {}, svg);
  el("rect", { x: W - 220, y: 24, width: 200, height: 92, rx: 6, fill: "#fff", stroke: css("--line"), "stroke-width": 3 }, win);
  [W - 175, W - 90].forEach(x => {
    const b = 108;
    el("path", { d: `M${x - 16},${b} L${x},${b - 64} L${x + 16},${b} M${x - 11},${b - 22} L${x + 11},${b - 22} M${x - 6},${b - 42} L${x + 6},${b - 42} M${x - 22},${b - 50} L${x + 22},${b - 50}`, stroke: css("--muted"), "stroke-width": 1.6, fill: "none" }, win);
  });
  el("path", { d: `M${W - 215},62 Q${W - 133},78 ${W - 25},62`, stroke: css("--muted"), "stroke-width": 1, fill: "none" }, win);
  // bảng trắng với cây lộ trình mini
  const wb = el("g", {}, svg);
  el("rect", { x: 30, y: 26, width: 170, height: 104, rx: 6, fill: "#fff", stroke: css("--line"), "stroke-width": 3 }, wb);
  el("text", { x: 42, y: 44, "font-size": 11, "font-weight": 700, fill: css("--ink") }, wb).textContent = "Lộ trình nghiên cứu";
  const pts = [[50, 86], [96, 62], [96, 86], [96, 110], [148, 54], [148, 70], [148, 100], [148, 118]];
  [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [3, 6], [3, 7]].forEach(([a, b]) => el("path", { d: `M${pts[a][0]},${pts[a][1]} C${(pts[a][0] + pts[b][0]) / 2},${pts[a][1]} ${(pts[a][0] + pts[b][0]) / 2},${pts[b][1]} ${pts[b][0]},${pts[b][1]}`, stroke: css("--primary-2"), fill: "none", "stroke-width": 1.4 }, wb));
  pts.forEach(([x, y], i) => el("circle", { cx: x, cy: y, r: i ? 3.5 : 5, fill: i ? css("--primary-2") : css("--accent") }, wb));
  const boss = team.find(p => p.key === "director");
  const staff = team.filter(p => p.key !== "director");
  if (boss) person(svg, boss, 230, 250, true, onPick);
  staff.forEach((p, i) => person(svg, p, 320 + i * 108, 250, false, onPick));
}
