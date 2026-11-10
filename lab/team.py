"""Phòng R&D AI đa module: Trưởng phòng giao việc theo từng MODULE → chuyên viên (riêng của module + mượn khối dùng chung)
nghiên cứu bằng RAG → Trưởng phòng phản biện, tổng hợp báo cáo chu kỳ 3 ngày."""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import modules as M
from . import web as W
from .cloud import is_sensitive
from .knowledge import KnowledgeBase, format_context


@dataclass
class Task:
    member: str
    title: str
    question: str


EVIDENCE_RULES = (
    "QUY TẮC NGUỒN (bắt buộc):\n"
    "- Dùng CẢ tài liệu kho [S#] và nguồn Internet [W#]. Ưu tiên nguồn 🏛 Chính thức (website hãng, IEC/IEEE/CIGRE/ISO, "
    "EVN/EVNNPT, cơ quan nhà nước), rồi ✅ Uy tín (tạp chí ngành, nhà xuất bản khoa học). Nguồn ⚠️ Chưa xác minh chỉ dùng "
    "khi không có nguồn khác và phải nói rõ.\n"
    "- Mọi số liệu, số hiệu/phiên bản tiêu chuẩn, tên sản phẩm, tính năng, giá, ngày tháng phải kèm [S#] hoặc [W#]. "
    "Điều KHÔNG có trong nguồn thì KHÔNG nêu như sự thật – nếu cần thì ghi rõ 'CHƯA CÓ NGUỒN'. Tuyệt đối không bịa.\n"
    "- KHÔNG dừng ở câu 'không đủ tài liệu': trả lời phần các nguồn hỗ trợ được, rồi liệt kê phần chưa xác minh và "
    "nơi cụ thể để kiểm chứng (URL, tên tài liệu).\n"
    "- Nguồn mâu thuẫn nhau thì nêu cả hai và nói nguồn nào đáng tin hơn.")


def web_appendix(body: str, wr: "W.WebResearch | None", evidence: str, question: str = "") -> str:
    """Thêm danh sách nguồn web + cảnh báo các số liệu/tiêu chuẩn không thấy trong nguồn nào."""
    out = body
    if wr and wr.sources:
        out += "\n\n## Nguồn Internet\n" + wr.markdown()
    miss = W.verify_claims(body, evidence, question)
    if miss:
        out += ("\n\n## 🔎 Kiểm chứng tự động\nCác chi tiết sau KHÔNG tìm thấy trong nguồn đã đọc – coi là CHƯA XÁC MINH, "
                "cần kiểm tra trước khi dùng: " + ", ".join(f"`{m}`" for m in miss))
    if wr and not wr.sources and wr.errors:
        out += "\n\n_Không tra được Internet lần này (" + "; ".join(wr.errors[:3]) + ")._"
    return out


@dataclass
class MemberReport:
    member: str
    name: str
    task: Task
    body: str
    sources: list[str] = field(default_factory=list)
    sensitive: bool = False
    engine: str = "local"


class Member:
    def __init__(self, key: str, spec: dict, common_rules: str, llm, kb: KnowledgeBase, top_k: int = 8,
                 sensitive_paths: list[str] | None = None, module_ctx: str = ""):
        self.key, self.spec, self.llm, self.kb, self.top_k = key, spec, llm, kb, top_k
        self.sensitive_paths = sensitive_paths or []
        self.module = spec.get("module", "shared")
        self.system = (f"{common_rules}\n\nVai trò của bạn: {spec['name']}"
                       f"{' (module ' + spec.get('module_name', '') + ')' if self.module != 'shared' else ' (khối dùng chung)'}.\n"
                       f"Phạm vi: {spec.get('scope', '')}.\nTiêu chuẩn/tài liệu nền cần bám: {', '.join(spec.get('references', []))}."
                       + (f"\n\n{module_ctx}" if module_ctx else ""))

    def work(self, task: Task, context_note: str = "", keywords: str = "", web: bool = True, web_get=None) -> MemberReport:
        hits = self.kb.search(f"{task.title}. {task.question} {keywords}".strip(), k=self.top_k)
        sens = is_sensitive([h.source for h in hits], self.sensitive_paths)
        wr = None
        if web:
            refs = " ".join(self.spec.get("references", [])[:3])
            wr = W.research(task.question, f"{keywords} {refs}".strip(), get=web_get or W.http_get, safe_only_keywords=sens)
        prompt = (f"NHIỆM VỤ CHU KỲ: {task.title}\nCÂU HỎI: {task.question}\n{context_note}\n\n"
                  f"TÀI LIỆU TRONG KHO:\n{format_context(hits)}\n\n"
                  f"NGUỒN INTERNET (đã tra lúc này):\n{wr.context() if wr else '(không tra web)'}\n\n{EVIDENCE_RULES}\n\n"
                  "Viết báo cáo mảng của bạn (markdown, ≤ 600 từ) gồm: 1) Kết luận chính – điểm MỚI tìm được; 2) Phân tích kỹ thuật "
                  "có trích [S#]/[W#]; 3) Ý nghĩa cho VTI (giải pháp, cạnh tranh, khả thi tại VN); 4) Điều chưa xác minh & nơi kiểm chứng.")
        body = self.llm.chat(self.system, prompt, role=self.key, sensitive=sens)
        engine = getattr(self.llm, "last_engine", "local")
        evidence = "\n".join(h.text for h in hits) + "\n" + (wr.all_text() if wr else "")
        body = web_appendix(body, wr, evidence, task.question)
        srcs = [f"[S{i}] {Path(h.source).name} – tr.{h.page}" for i, h in enumerate(hits, 1)]
        srcs += [f"[{w.id}] {w.title} – {w.url}" for w in (wr.sources if wr else [])]
        return MemberReport(self.key, self.spec["name"], task, body, srcs, sens, engine)


class Director:
    def __init__(self, cfg_team: dict, settings: dict, llm, kb: KnowledgeBase, modules: dict | None = None):
        self.team, self.settings, self.llm, self.kb = cfg_team, settings, llm, kb
        self.mods = M.load() if modules is None else modules
        self.web_enabled = W.load_cfg().get("enabled", True)
        self.web_get = W.http_get  # thay được trong test
        d = cfg_team["director"]
        self.system = f"{cfg_team['common_rules']}\n\nVai trò của bạn: {d['name']}.\n{d['mission']}"
        top_k = settings["rag"]["top_k"]
        sens_paths = (settings.get("cloud") or {}).get("sensitive_paths", [])
        self.members = {}
        for k, v in M.roster(cfg_team, self.mods).items():
            ctx = M.context(self.mods.get(v["module"]), v["module"]) if v["module"] != "shared" else ""
            self.members[k] = Member(k, v, cfg_team["common_rules"], llm, kb, top_k, sens_paths, ctx)

    def active_modules(self) -> list[str]:
        return [mid for mid, m in self.mods.items() if m.get("status", "active") == "active"]

    def module_keywords(self, mid: str | None) -> str:
        return " ".join((self.mods.get(mid) or {}).get("keywords", [])) if mid else ""

    # 1) Lập kế hoạch cho 1 module
    def plan_module(self, mid: str, focus: str = "", backlog: str = "") -> list[Task]:
        mod = self.mods[mid]
        keys = [k for k in M.module_members(self.mods, self.team, mid) if k in self.members]
        own = [k for k in keys if self.members[k].module == mid]
        roster = "\n".join(f"- {k}{' (dùng chung)' if k not in own else ''}: {self.members[k].spec['name']} – "
                           f"{self.members[k].spec.get('scope', '')}; câu hỏi thường trực: "
                           f"{'; '.join(self.members[k].spec.get('standing_questions', []))}" for k in keys)
        prompt = (f"{M.context(mod, mid)}\nTrọng tâm do anh Khương giao: {focus or '(không có – tự đề xuất theo lộ trình)'}\n"
                  f"Tồn đọng chu kỳ trước:\n{backlog or '(không có)'}\n\nNhân sự có thể giao:\n{roster}\n\n"
                  "Chu kỳ dài 3 ngày. Giao đúng 1 nhiệm vụ cụ thể, đo được cho MỖI chuyên viên riêng của module và tối đa 2 "
                  "chuyên viên dùng chung thật cần thiết. Ưu tiên điều MỚI, chưa nghiên cứu. Trả JSON dạng "
                  '[{"member":"<key>","title":"...","question":"..."}]')
        try:
            items = self.llm.chat_json(self.system, prompt, role="director")
            tasks = [Task(i["member"], i["title"], i["question"]) for i in items if i.get("member") in keys]
        except Exception:
            tasks = []
        shared_n = 0
        uniq: list[Task] = []
        for t in tasks:  # bỏ trùng, giới hạn 2 người dùng chung
            if any(u.member == t.member for u in uniq):
                continue
            if t.member not in own:
                if shared_n >= 2:
                    continue
                shared_n += 1
            uniq.append(t)
        have = {t.member for t in uniq}
        for k in own:  # đảm bảo chuyên viên riêng nào cũng có việc
            if k not in have:
                m = self.members[k]
                q = (m.spec.get("standing_questions") or [m.spec.get("scope", "")])[0]
                uniq.append(Task(k, f"Nghiên cứu thường trực – {m.spec['name']}", q))
        return uniq

    # Giữ tương thích: kế hoạch cho mọi module đang hoạt động
    def plan_week(self, focus: str = "", backlog: str = "") -> list[Task]:
        return [t for mid in self.active_modules() for t in self.plan_module(mid, focus, backlog)]

    # 2) Giao việc + 3) phản biện + 4) tổng hợp – chu kỳ 3 ngày cho các module đang hoạt động
    def run_cycle(self, focus: str = "", modules: list[str] | None = None, log=print, new_docs: list[str] | None = None,
                  highlights: str = "", day: str | None = None) -> Path:
        day = day or dt.date.today().isoformat()
        mids = [m for m in (modules or self.active_modules()) if m in self.mods]
        out_dir = Path(self.settings["paths"]["reports"]) / "cycles" / day
        out_dir.mkdir(parents=True, exist_ok=True)
        plan, reports = {}, {}
        for mid in mids:
            mod = self.mods[mid]
            log(f"■ Module {mod.get('icon', '')} {mod.get('name', mid)}")
            tasks = self.plan_module(mid, focus)
            plan[mid] = [t.__dict__ for t in tasks]
            reports[mid] = []
            (out_dir / mid).mkdir(exist_ok=True)
            for t in tasks:
                log(f"  → {t.member}: {t.title}")
                r = self.members[t.member].work(t, M.context(mod, mid), self.module_keywords(mid),
                                                web=self.web_enabled, web_get=self.web_get)
                reports[mid].append(r)
                (out_dir / mid / f"{t.member}.md").write_text(
                    f"# {mod.get('icon', '')} {mod.get('name', mid)} · {r.name}\n\n**Nhiệm vụ:** {t.title}\n\n"
                    f"**Câu hỏi:** {t.question}\n\n_Engine: {r.engine}{' · dữ liệu nhạy cảm → local' if r.sensitive else ''}_\n\n"
                    f"{r.body}\n\n## Nguồn trong kho\n" + "\n".join(f"- {s}" for s in r.sources), encoding="utf-8")
        (out_dir / "00_ke_hoach.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        path = out_dir / "BAO_CAO_3_NGAY.md"
        path.write_text(self.synthesize_cycle(reports, new_docs or [], highlights, day), encoding="utf-8")
        log(f"✓ Báo cáo 3 ngày: {path}")
        return path

    def run_week(self, focus: str = "", backlog: str = "", log=print) -> Path:  # tương thích lệnh cũ
        return self.run_cycle(focus, log=log)

    def synthesize_cycle(self, reports: dict[str, list[MemberReport]], new_docs: list[str], highlights: str, day: str) -> str:
        parts = []
        for mid, rs in reports.items():
            mod = self.mods[mid]
            ph = M.phase_now(mod, day)
            body = "\n\n".join(f"#### {r.name}\nNhiệm vụ: {r.task.title}\n{r.body.split(chr(10) + '## Nguồn Internet')[0][:2500]}\n"
                                 f"Nguồn web của {r.name}: " + "; ".join(x for x in r.sources if x.startswith("[W")) for r in rs)
            parts.append(f"### MODULE {mod.get('icon', '')} {mod.get('name', mid)} – {ph['code']} {ph['name']} "
                         f"({round(ph['pct'] * 100)}% thời gian giai đoạn)\n{body}")
        sections = "\n".join(f"## {s}" for s in self.team["director"]["report_sections"])
        docs = "\n".join(f"- {d}" for d in new_docs) or "(không có tài liệu mới)"
        prompt = (f"Báo cáo của các chuyên viên trong chu kỳ 3 ngày, theo module:\n\n{chr(10).join(parts)}\n\n"
                  f"Tài liệu mới vào kho kể từ chu kỳ trước:\n{docs}\n\nTin/cơ hội nổi bật từ bản tin năng lượng:\n"
                  f"{highlights or '(không có)'}\n\nPhản biện: chỉ ra nhận định thiếu nguồn hoặc mâu thuẫn giữa các chuyên viên. "
                  "Sau đó viết BÁO CÁO 3 NGÀY gửi anh Khương, tập trung vào những gì MỚI nghiên cứu/bổ sung được, "
                  f"theo đúng các mục:\n{sections}\nTrong mục theo module, dùng '### <icon> <tên module>' cho từng module. "
                  "Giữ trích dẫn nguồn của chuyên viên (ghi rõ URL cho nguồn web); điều chuyên viên ghi CHƯA XÁC MINH thì giữ nguyên "
                  "nhãn, không biến thành khẳng định; không thêm số liệu không có trong báo cáo chuyên viên. "
                  "Cuối báo cáo thêm mục '## Phản biện nội bộ'.")
        sens = any(r.sensitive for rs in reports.values() for r in rs)
        text = self.llm.chat(self.system, prompt, role="director", sensitive=sens)
        status = "\n".join(f"| {m.get('icon', '')} {m.get('name', k)} | {M.STATUS_VI.get(m.get('status', 'active'))} | "
                           f"{M.phase_now(m, day)['code']} {M.phase_now(m, day)['name']} |" for k, m in self.mods.items())
        d = dt.date.fromisoformat(day).strftime("%d/%m/%Y")
        web_src = sorted({x.split("] ", 1)[1] for rs in reports.values() for r in rs for x in r.sources if x.startswith("[W")})
        evidence = "\n".join(r.body for rs in reports.values() for r in rs)
        miss = W.verify_claims(text, evidence + "\n" + highlights + "\n" + "\n".join(new_docs))
        tail = ("\n\n## 🔎 Kiểm chứng tự động\nKhông thấy trong báo cáo chuyên viên/nguồn – coi là CHƯA XÁC MINH: "
                + ", ".join(f"`{m}`" for m in miss)) if miss else ""
        src = ("\n\n## Nguồn Internet đã tra trong chu kỳ\n" + "\n".join(f"- {x}" for x in web_src)) if web_src else ""
        return (f"# Báo cáo 3 ngày Phòng R&D – {d}\n\n> Module trong chu kỳ: "
                f"{', '.join(self.mods[m].get('name', m) for m in reports)}\n\n{text}{tail}{src}\n\n"
                f"## Trạng thái các module\n| Module | Trạng thái | Giai đoạn |\n|---|---|---|\n{status}\n")

    # Hỏi nhanh: chọn chuyên viên phù hợp, tra kho 1 lần, trả lời THẲNG câu hỏi (không theo khuôn báo cáo tuần)
    def route(self, question: str, module: str | None = None) -> tuple[list[str], str]:
        """Chọn chuyên viên + sinh từ khóa tiếng Anh để tìm trong tài liệu gốc (IEC/CIGRE đều bằng tiếng Anh)."""
        pool = M.module_members(self.mods, self.team, module) if module in self.mods else list(self.members)
        keys = ", ".join(f"{k} ({self.members[k].spec.get('scope', '')})" for k in pool if k in self.members)
        try:
            r = self.llm.chat_json(self.system, role="director", user=f"Câu hỏi: {question}\nChọn 1–2 chuyên viên phù hợp "
                                   f"nhất trong: {keys}. Đồng thời viết 5–12 từ khóa TIẾNG ANH chuyên ngành để tìm trong "
                                   "tiêu chuẩn IEC/IEEE/CIGRE (ví dụ: hot-spot temperature, loading guide, Duval triangle). "
                                   'Trả JSON {"members":["key"],"keywords_en":"..."}')
            mem = [k for k in r.get("members", []) if k in self.members][:2] or ["standards"]
            return mem, str(r.get("keywords_en", ""))[:300]
        except Exception:
            return ["standards"], ""

    def ask(self, question: str, members: list[str] | None = None, k: int | None = None, module: str | None = None,
            web: bool | None = None, log=lambda *_: None) -> str:
        chosen = [m for m in (members or []) if m in self.members]
        routed, kw = self.route(question, module)
        chosen = chosen or routed
        mid = module if module in self.mods else (self.members[chosen[0]].module if chosen[0] in self.members else None)
        mid = mid if mid in self.mods else None
        hits = self.kb.search(f"{question} {kw}".strip(), k=k or self.settings["rag"]["top_k"] + 4)
        experts = "\n".join(f"- {self.members[c].spec['name']}: {self.members[c].spec.get('scope', '')}" for c in chosen)
        ctx = format_context(hits) if hits else "(KHO TÀI LIỆU KHÔNG CÓ ĐOẠN NÀO LIÊN QUAN)"
        sens = is_sensitive([h.source for h in hits], self.members[chosen[0]].sensitive_paths)
        wr = None
        if self.web_enabled if web is None else web:
            log("Đang tra Internet (ưu tiên website chính thức)…")
            # dữ liệu khách hàng tham gia → chỉ gửi từ khóa kỹ thuật chung ra Internet
            wr = W.research(question, kw or self.module_keywords(mid), get=self.web_get, log=log, safe_only_keywords=sens)
        prompt = (f"{M.context(self.mods.get(mid), mid) if mid else ''}\n\n"
                  f"CÂU HỎI CỦA ANH KHƯƠNG: {question}\n\nChuyên môn được giao trả lời:\n{experts}\n\n"
                  f"TÀI LIỆU TRONG KHO:\n{ctx}\n\nNGUỒN INTERNET (vừa tra):\n{wr.context() if wr else '(không tra web)'}\n\n"
                  f"{EVIDENCE_RULES}\n\nYÊU CẦU TRẢ LỜI:\n"
                  "- Trả lời TRỰC TIẾP đúng câu hỏi. KHÔNG viết dạng báo cáo tuần/báo cáo 3 ngày, KHÔNG chào hỏi, KHÔNG tự giới thiệu.\n"
                  "- Cấu trúc: '## Trả lời ngắn' (3–6 dòng) → '## Chi tiết' (dùng bảng nếu là so sánh; có số liệu, "
                  "tên tiêu chuẩn, phiên bản, mỗi ý có [S#]/[W#]) → '## Độ tin cậy & nguồn' (nguồn chính thức nào, mức chắc chắn) "
                  "→ '## Chưa xác minh & cần bổ sung' (điều chưa có nguồn, gợi ý URL/tài liệu cụ thể để kiểm chứng).")
        body = self.llm.chat(self.system, prompt, role=chosen[0], sensitive=sens)
        evidence = "\n".join(h.text for h in hits) + "\n" + (wr.all_text() if wr else "")
        if hits:
            body += "\n\n## Nguồn trong kho\n" + "\n".join(
                f"- [S{i}] {Path(h.source).name} – tr.{h.page}" for i, h in enumerate(hits, 1))
        return web_appendix(body, wr, evidence, question)
