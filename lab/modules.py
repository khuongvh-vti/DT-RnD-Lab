"""Quản lý MODULE nghiên cứu của Phòng R&D (config/modules.yaml).

Mỗi module có: mục tiêu, phạm vi, lộ trình giai đoạn, chuyên viên riêng (members), danh sách chuyên viên dùng chung
được mượn (shared – khai báo trong config/team.yaml), thư mục tài liệu riêng trong library/ và trạng thái
active / standby / paused. Module mới tạo từ form trong app: Trưởng phòng (Qwen) thiết kế nhóm chuyên viên + lộ trình;
nếu Qwen chưa chạy thì dùng khung mặc định để anh sửa sau.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import re
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "config" / "modules.yaml"
STATUSES = ("active", "standby", "paused")
STATUS_VI = {"active": "Đang nghiên cứu", "standby": "Chờ kích hoạt", "paused": "Tạm dừng"}

HEADER = """# Các MODULE nghiên cứu của Phòng R&D VTI (file do app cập nhật – có thể sửa tay).
# status: active = đang nghiên cứu (chạy trong chu kỳ báo cáo 3 ngày) | standby = đã dựng khung, chờ kích hoạt | paused = tạm dừng
# Chuyên viên KHỐI DÙNG CHUNG nằm trong config/team.yaml; "shared" liệt kê những người module được mượn.
"""

# Tên & ngoại hình cho chuyên viên mới (8 người ban đầu giữ nguyên trong lab/site_content.TEAM)
NAMES = ["Hùng", "Trang", "Phong", "Thảo", "Quân", "Ngọc", "Dũng", "Hà", "Khoa", "Vy", "Long", "Mai", "Tùng", "Linh",
         "Sơn", "Yến", "Đạt", "Nhung", "Huy", "Thu"]
SKINS = ["#F1C7A1", "#E9B98F", "#D9A47A", "#F3D2B3", "#C98E64"]
HAIRS = ["#2B2118", "#3A2A20", "#1B1B1B", "#5A3A22", "#4A3426"]
STYLES = ["side", "bun", "buzz", "long", "bob", "default"]
SHIRTS = ["#1F3A5F", "#3E7C74", "#8B5CF6", "#C2410C", "#0E7490", "#BE185D", "#4D7C0F", "#7C3AED", "#B45309", "#0F766E"]


def _h(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def persona(key: str, base: dict | None = None) -> dict:
    """Ngoại hình ổn định theo key (để office/avatar vẽ được mọi chuyên viên mới)."""
    if base:
        return base
    h = _h(key)
    return {"key": key, "name": NAMES[h % len(NAMES)],
            "look": {"skin": SKINS[h % 5], "hair": HAIRS[(h // 5) % 5], "style": STYLES[(h // 25) % 6],
                     "shirt": SHIRTS[(h // 150) % 10], "glasses": bool((h // 1500) % 2)}}


def personas(keys: list[str], base: dict[str, dict]) -> dict[str, dict]:
    """Gán ngoại hình + tên KHÔNG trùng cho cả phòng (8 người ban đầu giữ nguyên tên)."""
    taken = {b["name"] for b in base.values()}
    out = {}
    for k in keys:
        if k in base:
            out[k] = base[k]
            continue
        p = persona(k)
        if p["name"] in taken:
            start = _h(k) % len(NAMES)
            free = [NAMES[(start + i) % len(NAMES)] for i in range(len(NAMES)) if NAMES[(start + i) % len(NAMES)] not in taken]
            p["name"] = free[0] if free else f"{p['name']} {len(taken)}"
        taken.add(p["name"])
        out[k] = p
    return out


def load(path: Path | str | None = None) -> dict:
    p = Path(path or MOD_PATH)
    if not p.exists():
        return {}
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("modules", {}) or {}


def save(mods: dict, path: Path | str | None = None):
    p = Path(path or MOD_PATH)
    body = yaml.safe_dump({"modules": mods}, allow_unicode=True, sort_keys=False, width=140)
    p.write_text(HEADER + "\n" + body, encoding="utf-8")


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFD", name.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return (s[:24].strip("_") or "module")


def phase_now(mod: dict, today: str | None = None) -> dict:
    phases = mod.get("phases") or []
    today = today or dt.date.today().isoformat()
    if not phases:
        return {"code": "—", "name": "Chưa đặt lộ trình", "start": today, "end": today, "pct": 0, "days_left": 0, "all": []}
    cur = next((p for p in phases if p["start"] <= today <= p["end"]), None)
    if cur is None:
        cur = phases[0] if today < phases[0]["start"] else phases[-1]
    a, b, t = (dt.date.fromisoformat(x) for x in (cur["start"], cur["end"], today))
    pct = max(0.0, min(1.0, (t - a).days / max(1, (b - a).days)))
    return {**cur, "pct": round(pct, 3), "days_left": max(0, (b - t).days), "all": phases}


def roster(team: dict, mods: dict, only: list[str] | None = None) -> dict[str, dict]:
    """Toàn bộ chuyên viên: khối dùng chung + chuyên viên riêng của từng module (key duy nhất)."""
    out = {k: {**v, "module": "shared", "module_name": "Khối dùng chung"} for k, v in team.get("members", {}).items()}
    for mid, m in mods.items():
        if only and mid not in only:
            continue
        for k, v in (m.get("members") or {}).items():
            out[k] = {**v, "module": mid, "module_name": m.get("name", mid)}
    return out


def module_members(mods: dict, team: dict, mid: str) -> list[str]:
    m = mods.get(mid) or {}
    own = list((m.get("members") or {}).keys())
    shared = [k for k in (m.get("shared") or []) if k in team.get("members", {})]
    return own + shared


def module_of(mods: dict, key: str) -> str | None:
    return next((mid for mid, m in mods.items() if key in (m.get("members") or {})), None)


def context(mod: dict | None, mid: str = "") -> str:
    if not mod:
        return ""
    ph = phase_now(mod)
    qs = "; ".join(mod.get("questions") or [])
    return (f"BỐI CẢNH MODULE [{mod.get('icon', '')} {mod.get('name', mid)}]\n- Mục tiêu: {mod.get('goal', '')}\n"
            f"- Phạm vi: {mod.get('scope', '')}\n- Giai đoạn hiện tại: {ph['code']} {ph['name']} ({ph['start']} → {ph['end']})\n"
            f"- Câu hỏi nghiên cứu chính: {qs}")


def set_status(mid: str, status: str, path=None) -> dict:
    if status not in STATUSES:
        raise ValueError("status")
    mods = load(path)
    if mid not in mods:
        raise KeyError(mid)
    mods[mid]["status"] = status
    save(mods, path)
    return mods[mid]


# ------------------------------------------------------------------ tạo module mới từ form
def _template(form: dict, mid: str) -> dict:
    """Khung mặc định khi chưa có Qwen: 2 chuyên viên (công nghệ & ứng dụng) + 3 giai đoạn."""
    name, refs = form["name"], [r.strip() for r in re.split(r"[,;\n]", form.get("references", "")) if r.strip()]
    start = dt.date.fromisoformat(form.get("start") or dt.date.today().isoformat())
    end = dt.date.fromisoformat(form["deadline"]) if form.get("deadline") else start + dt.timedelta(days=150)
    span = max(30, (end - start).days)
    cut = [start + dt.timedelta(days=round(span * f)) for f in (0, 0.35, 0.7, 1.0)]
    qs = [q.strip("-• ").strip() for q in form.get("questions", "").splitlines() if q.strip()]
    return {
        "phases": [
            {"code": "GĐ1", "name": "Nền tảng tri thức & tiêu chuẩn", "start": cut[0].isoformat(), "end": cut[1].isoformat()},
            {"code": "GĐ2", "name": "Thị trường, sản phẩm & đối thủ", "start": (cut[1] + dt.timedelta(days=1)).isoformat(), "end": cut[2].isoformat()},
            {"code": "GĐ3", "name": "Định hình giải pháp cho VTI", "start": (cut[2] + dt.timedelta(days=1)).isoformat(), "end": cut[3].isoformat()},
        ],
        "members": {
            f"{mid}_tech": {"name": f"Chuyên viên Công nghệ – {name}", "scope": form.get("scope") or name,
                            "references": refs or ["(cần bổ sung tiêu chuẩn)"],
                            "standing_questions": qs[:2] or [f"Công nghệ cốt lõi và tiêu chuẩn chính của {name} là gì?"]},
            f"{mid}_app": {"name": f"Chuyên viên Ứng dụng & Thị trường – {name}",
                           "scope": f"Ứng dụng tại Việt Nam, khách hàng, sản phẩm thị trường, cơ hội cho VTI ({name})",
                           "references": ["EVN/EVNNPT", "Quy hoạch điện VIII điều chỉnh"],
                           "standing_questions": qs[2:4] or [f"Khách hàng nào tại Việt Nam cần {name} và VTI tham gia ở vai trò nào?"]},
        },
        "questions": qs or [f"VTI nên tham gia {name} ở phần việc nào?"],
    }


def design_prompt(form: dict, existing_keys: list[str]) -> str:
    return (f"Anh Khương muốn mở MODULE NGHIÊN CỨU mới cho Phòng R&D VTI.\nTên: {form['name']}\n"
            f"Mục tiêu: {form.get('goal', '')}\nPhạm vi: {form.get('scope', '')}\n"
            f"Câu hỏi nghiên cứu chính: {form.get('questions', '')}\nTiêu chuẩn/tài liệu gợi ý: {form.get('references', '')}\n"
            f"Bắt đầu: {form.get('start') or dt.date.today().isoformat()} · Hạn: {form.get('deadline') or '(tự đề xuất, ~5 tháng)'}\n"
            f"Chuyên viên dùng chung sẵn có: standards, data_ai, ot_cyber, benchmark, vn_market. Key đã dùng: {', '.join(existing_keys)}.\n"
            "Thiết kế: 2–4 chuyên viên RIÊNG cho module (key snake_case tiếng Anh, không trùng), mỗi người có name, scope, "
            "references (tiêu chuẩn IEC/IEEE/CIGRE… CÓ THẬT, không bịa số hiệu – nếu không chắc thì ghi tên tổ chức), "
            "standing_questions (2 câu); 3–4 giai đoạn (code GĐ1.., name, start, end dạng YYYY-MM-DD); 2–4 câu hỏi nghiên cứu "
            "chính; 4–8 keywords tiếng Anh; danh sách shared (chọn trong 5 key dùng chung). Trả JSON: "
            '{"members":{"key":{"name":"","scope":"","references":[],"standing_questions":[]}},"phases":[{"code":"","name":"","start":"","end":""}],'
            '"questions":[],"keywords":[],"shared":[]}')


def create(form: dict, team: dict, llm=None, log=print, path=None, root: Path | None = None) -> str:
    name = (form.get("name") or "").strip()
    if not name:
        raise ValueError("Thiếu tên module")
    mods = load(path)
    mid = slugify(form.get("id") or name)
    base, i = mid, 2
    while mid in mods:
        mid, i = f"{base}_{i}", i + 1
    used = list(roster(team, mods).keys())
    plan = _template(form, mid)
    if llm is not None:
        try:
            log("Trưởng phòng đang thiết kế nhóm chuyên viên & lộ trình cho module…")
            r = llm.chat_json("Bạn là Trưởng phòng R&D ngành điện, thiết kế tổ chức nghiên cứu.", design_prompt(form, used),
                              role="director")
            mem = {}
            for k, v in (r.get("members") or {}).items():
                k = slugify(k)
                if k in used or k in mem:
                    k = f"{mid}_{k}"
                if isinstance(v, dict) and v.get("name"):
                    mem[k] = {"name": str(v["name"]), "scope": str(v.get("scope", "")),
                              "references": [str(x) for x in v.get("references", [])][:8],
                              "standing_questions": [str(x) for x in v.get("standing_questions", [])][:3]}
            phases = [p for p in (r.get("phases") or []) if all(p.get(x) for x in ("code", "name", "start", "end"))]
            for p in phases:
                dt.date.fromisoformat(p["start"]), dt.date.fromisoformat(p["end"])
            if mem:
                plan["members"] = dict(list(mem.items())[:4])
            if phases:
                plan["phases"] = phases[:5]
            plan["questions"] = [str(x) for x in r.get("questions", [])][:4] or plan["questions"]
            plan["keywords"] = [str(x) for x in r.get("keywords", [])][:8]
            plan["shared"] = [x for x in r.get("shared", []) if x in team.get("members", {})]
        except Exception as e:  # Qwen chưa chạy / JSON lỗi → giữ khung mặc định
            log(f"Không dùng được Qwen ({type(e).__name__}) → dùng khung mặc định, anh sửa sau trong config/modules.yaml.")
    mods[mid] = {
        "name": name, "icon": (form.get("icon") or "🧪").strip()[:4], "status": form.get("status") or "active",
        "created": dt.date.today().isoformat(), "goal": form.get("goal", ""), "scope": form.get("scope", ""),
        "library": [f"m_{mid}"], "keywords": plan.get("keywords") or [],
        "shared": plan.get("shared") or ["standards", "data_ai", "benchmark", "vn_market"],
        "phases": plan["phases"], "questions": plan["questions"], "members": plan["members"],
    }
    save(mods, path)
    root = root or ROOT
    lib = root / "library" / f"m_{mid}"
    lib.mkdir(parents=True, exist_ok=True)
    (lib / "README.md").write_text(
        f"# Thư mục tài liệu module {name}\n\nĐặt PDF/MD/TXT của module **{name}** vào đây rồi bấm “Nạp vào kho”.\n"
        f"Mục tiêu: {form.get('goal', '')}\n", encoding="utf-8")
    rep = root / "reports" / "modules" / mid
    rep.mkdir(parents=True, exist_ok=True)
    (rep / "00_GIOI_THIEU_MODULE.md").write_text(intro_md(mid, mods[mid], team), encoding="utf-8")
    log(f"✓ Đã mở module {mid} – {len(plan['members'])} chuyên viên riêng, {len(plan['phases'])} giai đoạn.")
    return mid


def intro_md(mid: str, m: dict, team: dict) -> str:
    rows = "\n".join(f"| {k} | {v['name']} | {v.get('scope', '')} | {', '.join(v.get('references', []))} |"
                     for k, v in (m.get("members") or {}).items())
    ph = "\n".join(f"| {p['code']} | {p['name']} | {p['start']} | {p['end']} |" for p in m.get("phases", []))
    shared = ", ".join(team.get("members", {}).get(k, {}).get("name", k) for k in m.get("shared", []))
    qs = "\n".join(f"- {q}" for q in m.get("questions", []))
    return (f"# {m.get('icon', '')} Module {m['name']} – giới thiệu\n\n"
            f"> Mở ngày {m.get('created', '')} · trạng thái: {STATUS_VI.get(m.get('status'), m.get('status'))} · "
            f"thư mục tài liệu: `library/{(m.get('library') or ['m_' + mid])[0]}/`\n\n"
            f"## Mục tiêu\n{m.get('goal', '')}\n\n## Phạm vi\n{m.get('scope', '')}\n\n## Câu hỏi nghiên cứu chính\n{qs}\n\n"
            f"## Lộ trình\n| Giai đoạn | Nội dung | Bắt đầu | Kết thúc |\n|---|---|---|---|\n{ph}\n\n"
            f"## Nhân sự riêng của module\n| Key | Vai trò | Phạm vi | Tài liệu nền |\n|---|---|---|---|\n{rows}\n\n"
            f"## Mượn từ khối dùng chung\n{shared}\n")
